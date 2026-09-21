"""Private synthetic fixtures exercise import-download gates, never platform proof."""
import copy
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED

import solution_release as release


def archive(members):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as output:
        for name, value in members.items():
            output.writestr(name, value)
    return buffer.getvalue()


def synthetic_solution(role):
    members = {
        "solution.xml": (
            "<ImportExportXml><SolutionManifest><UniqueName>" + release.SOLUTION_NAMES[role]
            + "</UniqueName><Version>" + release.VERSION
            + "</Version><Managed>0</Managed></SolutionManifest></ImportExportXml>"
        ).encode(),
        "[Content_Types].xml": b"<Types/>",
    }
    states = "".join("<Workflow><StateCode>0</StateCode><StatusCode>1</StatusCode></Workflow>"
                     for _ in release.ACTION_COUNTS[role])
    refs = "".join(f'<connectionreference connectionreferencelogicalname="psr_SyntheticFixture{i}"/>'
                   for i in range(4 if role == "reviewer" else 6))
    members["customizations.xml"] = (
        "<ImportExportXml><Workflows>" + states + "</Workflows><connectionreferences>"
        + refs + "</connectionreferences></ImportExportXml>"
    ).encode()
    for i in range(8 if role == "reviewer" else 23):
        schema = f"psr_SyntheticConfiguration{i}"
        members[f"environmentvariabledefinitions/{schema}/environmentvariabledefinition.xml"] = (
            f'<environmentvariabledefinition schemaname="{schema}"><type>100000000</type>'
            "</environmentvariabledefinition>"
        ).encode()
    for i, count in enumerate(release.ACTION_COUNTS[role]):
        definition = {"actions": {
            "Synthetic" + str(j): {"type": "Compose", "inputs": "PRIVATE SYNTHETIC FIXTURE"}
            for j in range(count)
        }}
        if role == "automation":
            definition["parameters"] = {"psrDeploymentReady": {"type": "Bool", "defaultValue": False}}
        members[f"Workflows/fixture-{i}.json"] = json.dumps({
            "properties": {"definition": definition, "connectionReferences": {
                "fixture": {
                    "runtimeSource": "invoker" if count == 225 else "embedded",
                    "connection": {"connectionReferenceLogicalName": "psr_SyntheticFixture0"},
                },
            }},
        }).encode()
    if role == "reviewer":
        members["bots/psr_PowerPlatformSolutionReviewer/configuration.json"] = b'{"publishOnImport":false}'
        for i in range(19):
            members[f"botcomponents/fixture-{i}/data"] = b"kind: SyntheticFixture\n"
    return members


class ImportReleaseTests(unittest.TestCase):
    def setUp(self):
        holding = release.SITE / "_private-hold"
        holding.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="solution-download-unit-", dir=holding)
        self.addCleanup(temporary.cleanup)
        self.site = Path(temporary.name)
        self.members = {role: synthetic_solution(role) for role in ("reviewer", "automation")}
        self.members["support"] = {"README.txt": b"PRIVATE SYNTHETIC TEST FIXTURE"}
        self.data = {
            "schemaVersion": 1, "kind": "IMPORT_FIRST_UNMANAGED_SOLUTION_RELEASE",
            "version": release.VERSION, "approvedPublicDistribution": False,
            "evidence": {
                "sameTenantSandboxImportVerified": False, "automaticWordRuntimeVerified": False,
                "crossTenantInstallationVerified": False, "separateLeastPrivilegeRequesterVerified": False,
                "publishedDemoAgentChanged": False, "setupOrActivationPerformed": False,
            },
            "files": {}, "archiveMembers": {}, "nativeImports": [],
            "structuralIdentifiers": [], "structuralIdentifierMembers": {},
        }
        self.refresh()

    def refresh(self):
        for role, name in release.PATHS.items():
            value = archive(self.members[role]) if role in self.members else b"SYNTHETIC setup instructions\n"
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
            self.data["files"][role] = {"path": name, "bytes": len(value), "sha256": release.sha(value)}
        self.data["archiveMembers"] = {
            role: {name: {"bytes": len(value), "sha256": release.sha(value)} for name, value in members.items()}
            for role, members in self.members.items()
        }
        self.save()

    def save(self):
        (self.site / release.MANIFEST).write_text(json.dumps(self.data), encoding="utf-8")

    def test_candidate_is_not_native_or_public_approval(self):
        actual = release.verify(self.site, required=True)
        self.assertIn("has not been verified", release.card(actual))
        with self.assertRaisesRegex(ValueError, "Parent safety approval"):
            release.verify(self.site, publication=True)
        self.assertIn("Import first.", release.setup_section(actual))
        self.assertNotIn("target.zip", release.setup_section(actual))

    def test_same_origin_direct_solutions_are_primary(self):
        rendered = release.card(release.verify(self.site))
        for role in ("reviewer", "automation"):
            self.assertIn('class="button primary" href="' + release.PATHS[role], rendered)
        self.assertNotIn(".portable.template.zip", rendered)
        self.assertNotIn(".bundle.zip", rendered)

    def test_home_switches_downloads_without_rewriting_historical_proof(self):
        from build_home import build
        from build_walkthrough import PREFIX, verify as walkthrough
        import word_release
        shutil.copyfile(release.SITE / "index.html", self.site / "index.html")
        shutil.copytree(release.SITE / PREFIX, self.site / PREFIX)
        shutil.copytree(release.SITE / "reference", self.site / "reference")
        for name in word_release.PUBLIC_PATHS:
            destination = self.site / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(release.SITE / name, destination)
        provenance = walkthrough()
        first = build(provenance, self.site)
        (self.site / "index.html").write_text(first, encoding="utf-8")
        self.assertEqual(first, build(provenance, self.site))
        self.assertEqual(first.count('id="solution-download"'), 1)
        self.assertEqual(first.count('id="word-template-setup"'), 1)
        self.assertIn("automatic candidate", first)
        self.assertIn("not a separate least-privilege", first)
        self.assertNotIn("Configure and repack first.", first)
        self.assertNotIn("build a <code>*.target.zip", first)
        self.assertEqual(first.split("<body>")[0],
                         (release.SITE / "index.html").read_text(encoding="utf-8").split("<body>")[0])

    def test_no_manifest_does_not_invent_downloads(self):
        (self.site / release.MANIFEST).unlink()
        self.assertIsNone(release.verify(self.site))
        with self.assertRaises(ValueError):
            release.verify(self.site, required=True)

    def test_outer_bundle_cannot_be_a_solution(self):
        with self.assertRaisesRegex(ValueError, "not an outer bundle"):
            release.verify_solution(archive({"inside.zip": b"not a solution"}), "reviewer")

    def test_native_record_fragments_are_element_first_not_document_declarations(self):
        declaration = b'<?xml version="1.0" encoding="utf-8"?>\n'
        self.members["reviewer"]["solution.xml"] = declaration + self.members["reviewer"]["solution.xml"]
        self.refresh()
        release.verify(self.site)
        for prefix in release.RECORD_PREFIXES:
            with self.subTest(prefix=prefix):
                name = prefix + "synthetic-record.xml"
                self.members["reviewer"][name] = declaration + b"<SyntheticRecord/>"
                self.refresh()
                with self.assertRaisesRegex(ValueError, "must begin with an Element"):
                    release.verify(self.site)
                self.members["reviewer"].pop(name)

    def test_target_tokens_and_missing_logic_fail(self):
        self.members["reviewer"]["botcomponents/fixture-0/data"] = b"model: __PSR_MODEL_NAME__\n"
        self.refresh()
        with self.assertRaisesRegex(ValueError, "target substitution"):
            release.verify(self.site)
        self.members["reviewer"] = synthetic_solution("reviewer")
        self.members["reviewer"].pop("botcomponents/fixture-18/data")
        self.refresh()
        with self.assertRaisesRegex(ValueError, "component closure"):
            release.verify(self.site)

    def test_word_schema_keys_are_concrete(self):
        members = self.members["reviewer"]
        name = "Workflows/fixture-0.json"
        workflow = json.loads(members[name])
        action = workflow["properties"]["definition"]["actions"]["Synthetic0"]
        action["inputs"] = {"host": {"operationId": "CreateFileItem"}, "parameters": {
            "schema": "PSR_PRESENTATION_READER_V4_3",
        }}
        members[name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "four concrete schema roots"):
            release.verify(self.site)
        action["inputs"]["parameters"].update({f"dynamicFileSchema/wrong{i}": "" for i in range(4)})
        members[name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "four concrete schema roots"):
            release.verify(self.site)
        action["inputs"]["parameters"] = {key: "" for key in release.WORD_SCHEMA_KEYS}
        action["inputs"]["parameters"]["schema"] = "PSR_PRESENTATION_READER_V4_3"
        members[name] = json.dumps(workflow).encode()
        self.refresh()
        release.verify(self.site)

    def test_native_evidence_requires_both_exact_zip_hashes(self):
        self.data["evidence"]["sameTenantSandboxImportVerified"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "both exact ZIPs"):
            release.verify(self.site)
        self.data["nativeImports"] = [
            {"role": role, "status": "Succeeded", **dict.fromkeys(release.NATIVE_CHECKS, True),
             "sha256": self.data["files"][role]["sha256"]}
            for role in ("reviewer", "automation")
        ]
        self.save()
        actual = release.verify(self.site)
        self.assertIn("same-tenant sandbox", release.card(actual))
        self.data["nativeImports"][0]["sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ValueError, "both exact ZIPs"):
            release.verify(self.site)

    def test_import_success_without_definition_fidelity_cannot_be_published(self):
        self.data["approvedPublicDistribution"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "exact definition verification"):
            release.verify(self.site, publication=True)
        self.data["evidence"]["sameTenantSandboxImportVerified"] = True
        self.data["nativeImports"] = [
            {"role": role, "status": "Succeeded", **dict.fromkeys(release.NATIVE_CHECKS, True),
             "sha256": self.data["files"][role]["sha256"]}
            for role in ("reviewer", "automation")
        ]
        self.data["nativeImports"][1]["workflowDefinitionsVerified"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "verified definitions"):
            release.verify(self.site, publication=True)
        self.data["nativeImports"][1]["workflowDefinitionsVerified"] = True
        self.data["nativeImports"][1]["targetPrivateIdentity"] = "must-not-ship"
        self.save()
        with self.assertRaisesRegex(ValueError, "only sanitized"):
            release.verify(self.site, publication=True)

    def test_import_does_not_upgrade_historical_runtime_claims(self):
        baseline = copy.deepcopy(self.data)
        for key in baseline["evidence"]:
            if key == "sameTenantSandboxImportVerified":
                continue
            self.data = copy.deepcopy(baseline)
            self.data["evidence"][key] = True
            self.save()
            with self.assertRaisesRegex(ValueError, "runtime acceptance", msg=key):
                release.verify(self.site)

    def test_maker_fallback_and_connection_instances_rejected(self):
        name = "Workflows/fixture-1.json"
        workflow = json.loads(self.members["reviewer"][name])
        ref = workflow["properties"]["connectionReferences"]["fixture"]
        ref["runtimeSource"] = "embedded"
        self.members["reviewer"][name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "boundaries"):
            release.verify(self.site)
        ref["runtimeSource"] = "invoker"
        ref["connection"]["connectionName"] = "synthetic-forbidden-connection-instance"
        self.members["reviewer"][name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "packaged connection instances"):
            release.verify(self.site)

    def test_external_or_parent_download_paths_rejected(self):
        for path in ("../private.zip", "https://example.invalid/reviewer.zip"):
            self.data["files"]["reviewer"]["path"] = path
            self.save()
            with self.assertRaisesRegex(ValueError, "same-origin"):
                release.verify(self.site)

    def test_odata_property_is_not_a_mailbox_but_values_are_screened(self):
        from check_public import binding_screen_text, GENERIC
        field = "EnvironmentVariableDefinitionId" + "@odata.bind"
        value = "synthetic" + "@" + "example.invalid"
        raw = json.dumps({field: value})
        screened = binding_screen_text(raw)
        self.assertNotIn(field, screened)
        self.assertIn(value, screened)
        self.assertIsNotNone(re.search(GENERIC[1], screened))
        self.assertEqual(binding_screen_text(field), field)

    def test_auto_publication_and_truncated_automation_rejected(self):
        self.members["reviewer"]["bots/psr_PowerPlatformSolutionReviewer/configuration.json"] = b'{"publishOnImport":true}'
        self.refresh()
        with self.assertRaisesRegex(ValueError, "publication on import"):
            release.verify(self.site)
        self.members["reviewer"] = synthetic_solution("reviewer")
        name = "Workflows/fixture-0.json"
        workflow = json.loads(self.members["automation"][name])
        workflow["properties"]["definition"]["actions"].pop("Synthetic499")
        self.members["automation"][name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "every implemented workflow action"):
            release.verify(self.site)

    def test_stopped_unbound_unconfigured_defaults_are_required(self):
        baseline = copy.deepcopy(self.members)
        self.members["reviewer"]["customizations.xml"] = self.members["reviewer"]["customizations.xml"].replace(
            b"<StateCode>0</StateCode>", b"<StateCode>1</StateCode>", 1)
        self.refresh()
        with self.assertRaisesRegex(ValueError, "must be stopped"):
            release.verify(self.site)
        self.members = copy.deepcopy(baseline)
        self.members["reviewer"]["customizations.xml"] = self.members["reviewer"]["customizations.xml"].replace(
            b'psr_SyntheticFixture0"/>',
            b'psr_SyntheticFixture0"><connectionid>forbidden-instance</connectionid></connectionreference>')
        self.refresh()
        with self.assertRaisesRegex(ValueError, "present and unbound"):
            release.verify(self.site)
        self.members = copy.deepcopy(baseline)
        name = "Workflows/fixture-0.json"
        workflow = json.loads(self.members["automation"][name])
        workflow["properties"]["definition"]["parameters"]["psrDeploymentReady"]["defaultValue"] = True
        self.members["automation"][name] = json.dumps(workflow).encode()
        self.refresh()
        with self.assertRaisesRegex(ValueError, "readiness must remain false"):
            release.verify(self.site)

    def test_missing_native_configuration_definition_fails(self):
        self.members["reviewer"].pop(
            "environmentvariabledefinitions/psr_SyntheticConfiguration0/environmentvariabledefinition.xml")
        self.refresh()
        with self.assertRaisesRegex(ValueError, "configuration definitions"):
            release.verify(self.site)

    def test_preparation_validates_before_writing_public_downloads(self):
        import prepare_solution_release as prepare
        temporary = tempfile.TemporaryDirectory(prefix="p-", dir=release.SITE / "_private-hold")
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name)
        (destination / "downloads").mkdir()
        source = destination / "_private-hold" / "inputs"
        source.mkdir(parents=True)
        support = {**self.members["support"], "INSTALL.md": b"Synthetic private installation fixture.\n"}
        for role in ("reviewer", "automation", "support"):
            (source / Path(release.PATHS[role]).name).write_bytes(
                archive(support if role == "support" else self.members[role]))
        audit = source / "private-audit.json"
        audit.write_text(json.dumps({"privatePatternSet": ["synthetic-private-value-never-shipped"]}), encoding="utf-8")
        evidence = source / "invalid-evidence.json"
        evidence.write_text('[{"role":"reviewer","status":"Failed"}]', encoding="utf-8")
        with patch.object(release, "SITE", destination), patch.object(
                prepare, "verify_word", return_value={"structuralIdentifiers": []}):
            with self.assertRaisesRegex(ValueError, "Native receipts"):
                prepare.prepare(source, audit, evidence)
            self.assertEqual(list((destination / "downloads").iterdir()), [])
            result = prepare.prepare(source, audit)
        self.assertFalse(result["approvedPublicDistribution"])
        self.assertFalse(result["evidence"]["sameTenantSandboxImportVerified"])
        self.assertEqual(release.verify(destination), result)


if __name__ == "__main__":
    unittest.main()
