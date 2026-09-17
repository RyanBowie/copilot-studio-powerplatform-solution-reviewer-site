"""Synthetic private fixtures test publication gates; they are never public proof."""
import copy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image
import word_release as word


def archive(values):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as output:
        for name, value in values.items():
            output.writestr(name, value)
    return buffer.getvalue()


class WordReleaseTests(unittest.TestCase):
    def setUp(self):
        holding = word.SITE / "_private-hold"
        holding.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="word-public-unit-", dir=holding)
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        self.document = archive({
            "[Content_Types].xml": b"<Types/>",
            "word/document.xml": b"<document>SYNTHETIC PRIVATE UNIT FIXTURE</document>",
        })
        self.solution = archive({
            "solution.xml": b"<Solution/>", "customizations.xml": b"<Customizations/>",
            "Workflows/fixture.json": b'{"fixture":"shared_wordonlinebusiness PSR_PRESENTATION_READER_V4_3"}',
        })
        self.members = {
            "psr_PowerPlatformSolutionReviewer.portable.template.zip": self.solution,
            "psr_PowerPlatformSolutionAutomation.portable.template.zip": self.solution,
            "install.py": b"# Synthetic private unit fixture.\n",
            "target.example.json": b"{}", "install-manifest.json": b"{}",
            "template.docx": self.document,
        }
        image = io.BytesIO()
        Image.new("RGB", (400, 500), "white").save(image, format="PNG")
        values = {
            "bundle": archive(self.members), "template": self.document, "example": self.document,
            "setup": b"Synthetic private unit fixture - not installation proof.\n",
            "page1": image.getvalue(), "page2": image.getvalue(),
        }
        self.data = {
            "schemaVersion": 1, "kind": "REVIEWED_WORD_OUTPUT_CONFIGURABLE_RELEASE",
            "distributionVersion": word.VERSION, "layoutVersion": "4.3.1",
            "approvedPublicDerivatives": True,
            "packageKind": "PORTABLE_DERIVED_CONFIGURE_BEFORE_IMPORT",
            "evidence": {
                "fixture": "synthetic", "formatOnlyRegeneration": True,
                "nativeGenerationVerified": True, "wordWebPages": 2, "desktopWordPages": 2,
                "reviewContentPreserved": True, "requesterReadGrantVerified": True,
                "separateLeastPrivilegeAccountTested": False,
                "publishedDemoAgentUpdated": False, "automaticWordRunVerified": False,
                "crossTenantInstallationVerified": False, "wordOutlineHeadings": False,
            },
            "files": {}, "bundleMembers": {}, "structuralIdentifiers": [],
            "structuralIdentifierMembers": {},
        }
        for role, value in values.items():
            self.asset(role, value)
        self.member_pins()
        self.save()

    def asset(self, role, value):
        path = self.site / word.PATHS[role]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
        self.data["files"][role] = {"path": word.PATHS[role], "bytes": len(value), "sha256": word.sha(value)}

    def member_pins(self):
        self.data["bundleMembers"] = {
            name: {"bytes": len(value), "sha256": word.sha(value)} for name, value in self.members.items()
        }

    def save(self):
        (self.site / word.MANIFEST).write_text(json.dumps(self.data), encoding="utf-8")

    def test_complete_reviewed_closure_and_honest_page(self):
        release = word.verify(self.site, required=True)
        rendered = word.section(release, hero=True)
        self.assertIn('<h1 id="top">', rendered)
        self.assertIn("not a separate least-privilege", rendered)
        self.assertIn("automatic candidate", rendered)
        self.assertIn("No cross-tenant", rendered)
        self.assertIn(word.PATHS["bundle"], rendered)
        self.assertEqual(word.summary(release)["evidence"], self.data["evidence"])

    def test_home_integration_is_repeatable_and_removes_stale_current_claims(self):
        from build_home import build
        from build_walkthrough import verify, PREFIX
        shutil.copyfile(word.SITE / "index.html", self.site / "index.html")
        shutil.copytree(word.SITE / PREFIX, self.site / PREFIX)
        shutil.copytree(word.SITE / "reference", self.site / "reference")
        provenance = verify()
        first = build(provenance, self.site)
        (self.site / "index.html").write_text(first, encoding="utf-8")
        self.assertEqual(first, build(provenance, self.site))
        self.assertEqual(first.count('id="word-output"'), 1)
        self.assertEqual(first.count("<h1 "), 1)
        self.assertNotIn("No installer is included in this public preview", first)
        self.assertNotIn("Bind the five target connections", first)
        self.assertIn('id="word-template-setup"', first)
        self.assertIn('id="word-tool-reference"', first)
        self.assertIn("PSR_PRESENTATION_READER_V4_3", first)

    def test_missing_manifest_does_not_invent_word_release(self):
        (self.site / word.MANIFEST).unlink()
        self.assertIsNone(word.verify(self.site))
        with self.assertRaises(ValueError):
            word.verify(self.site, required=True)

    def test_false_approval_and_false_runtime_claims_fail(self):
        baseline = copy.deepcopy(self.data)
        for field in ("automaticWordRunVerified", "crossTenantInstallationVerified",
                      "publishedDemoAgentUpdated", "wordOutlineHeadings"):
            self.data = copy.deepcopy(baseline)
            self.data["evidence"][field] = True
            self.save()
            with self.assertRaises(ValueError, msg=field):
                word.verify(self.site)
        self.data = baseline
        self.data["approvedPublicDerivatives"] = False
        self.save()
        with self.assertRaises(ValueError):
            word.verify(self.site)

    def test_evidence_bool_is_not_numeric_attestation(self):
        self.data["evidence"]["nativeGenerationVerified"] = 1
        self.save()
        with self.assertRaises(ValueError):
            word.verify(self.site)

    def test_duplicate_json_keys_fail(self):
        path = self.site / word.MANIFEST
        path.write_text(path.read_text().replace('"schemaVersion": 1', '"schemaVersion": 1, "schemaVersion": 1'), encoding="utf-8")
        with self.assertRaises(ValueError):
            word.verify(self.site)

    def test_asset_hash_and_complete_member_closure_fail_closed(self):
        (self.site / word.PATHS["example"]).write_bytes(b"changed")
        with self.assertRaises(ValueError):
            word.verify(self.site)
        self.asset("example", self.document)
        self.data["bundleMembers"].pop("install.py")
        self.save()
        with self.assertRaises(ValueError):
            word.verify(self.site)

    def test_old_solution_cannot_be_relabelled_word_enabled(self):
        self.members["psr_PowerPlatformSolutionReviewer.portable.template.zip"] = archive({
            "solution.xml": b"<Solution/>", "customizations.xml": b"<Customizations/>",
        })
        self.asset("bundle", archive(self.members))
        self.member_pins()
        self.save()
        with self.assertRaisesRegex(ValueError, "missing the current Word"):
            word.verify(self.site)

    def test_exact_template_required_in_distribution(self):
        self.members["template.docx"] = b"not the template"
        self.asset("bundle", archive(self.members))
        self.member_pins()
        self.save()
        with self.assertRaisesRegex(ValueError, "exact public Word template"):
            word.verify(self.site)

    def test_unsafe_archive_members_and_macros_rejected(self):
        with self.assertRaises(ValueError):
            word.archive_members(archive({"../outside": b"x"}))
        with self.assertRaises(ValueError):
            word.archive_members(archive({"file.txt": b"x", "FILE.txt": b"y"}))
        with self.assertRaises(ValueError):
            word.verify_docx(archive({
                "[Content_Types].xml": b"<Types/>", "word/document.xml": b"<document/>",
                "word/vbaProject.bin": b"x",
            }))

    def test_asset_paths_cannot_redirect_to_private_or_remote_files(self):
        self.data["files"]["bundle"]["path"] = "../private.zip"
        self.save()
        with self.assertRaises(ValueError):
            word.verify(self.site)

    def test_identifier_exemptions_cannot_expand_to_unreviewed_members(self):
        self.data["structuralIdentifierMembers"] = {"other-file.txt": []}
        self.save()
        with self.assertRaisesRegex(ValueError, "exact reviewed archive-member"):
            word.verify(self.site)


if __name__ == "__main__":
    unittest.main()
