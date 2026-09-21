"""Verify import-first candidates separately from historical Word runtime evidence."""
import hashlib
import html
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

from word_release import archive_members, identifier_members, unique_object

SITE = Path(__file__).resolve().parents[1]
VERSION = "3.3.2.7"
MANIFEST = "downloads/solution-import-release.json"
PATHS = {
    "reviewer": f"downloads/psr_PowerPlatformSolutionReviewer_3_3_2_7_unmanaged.zip",
    "automation": f"downloads/psr_PowerPlatformSolutionAutomation_3_3_2_7_unmanaged.zip",
    "support": f"downloads/solution-reviewer-setup-{VERSION}.zip",
    "setup": "downloads/SOLUTION-IMPORT-SETUP.md",
}
SOLUTION_NAMES = {
    "reviewer": "psr_PowerPlatformSolutionReviewer",
    "automation": "psr_PowerPlatformSolutionAutomation",
}
ACTION_COUNTS = {"reviewer": [21, 225], "automation": [500]}
TOKEN = re.compile(r"__(?:PSR|TARGET)_[A-Z0-9_]+__")
RECORD_PREFIXES = ("bots/", "botcomponents/", "Assets/", "environmentvariabledefinitions/")
WORD_SCHEMA_KEYS = {f"dynamicFileSchema/{value}" for value in ("940007", "940008", "940009", "940010")}
NATIVE_CHECKS = {
    "flowsStopped", "agentUnpublished", "componentClosureVerified",
    "workflowDefinitionsVerified", "unboundReferencesVerified",
    "emptyConfigurationVerified", "identityBoundariesVerified", "nativeChannelConfigurationAbsent",
}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def flatten(actions):
    if not isinstance(actions, dict):
        raise ValueError("Workflow actions must be an object.")
    result = []
    for action in actions.values():
        if not isinstance(action, dict) or not isinstance(action.get("type"), str):
            raise ValueError("Invalid workflow action.")
        result.append(action)
        for container in (action, action.get("else", {}), action.get("default", {})):
            if "actions" in container:
                result.extend(flatten(container["actions"]))
        for case in action.get("cases", {}).values():
            result.extend(flatten(case.get("actions", {})))
    return result


def verify_solution(data, role):
    members = archive_members(data)
    if not {"solution.xml", "customizations.xml", "[Content_Types].xml"} <= members.keys():
        raise ValueError("A direct download must be a solution, not an outer bundle.")
    manifest = ET.fromstring(members["solution.xml"]).find("SolutionManifest")
    if (manifest is None or manifest.findtext("UniqueName") != SOLUTION_NAMES[role]
            or manifest.findtext("Version") != VERSION or manifest.findtext("Managed") != "0"):
        raise ValueError("Unexpected unmanaged solution identity/version.")
    for name, value in members.items():
        text = value.decode("utf-8-sig")
        if TOKEN.search(text):
            raise ValueError("Import-first solutions cannot contain target substitution tokens: " + name)
        if name.endswith(".xml"):
            ET.fromstring(value)
            if name.startswith(RECORD_PREFIXES) and not re.match(r"<[A-Za-z_]", text.lstrip()):
                raise ValueError("Native source-control record fragments must begin with an Element: " + name)
    customizations = ET.fromstring(members["customizations.xml"])
    states = customizations.findall("./Workflows/Workflow")
    if (len(states) != len(ACTION_COUNTS[role])
            or any(row.findtext("StateCode") != "0" or row.findtext("StatusCode") != "1" for row in states)):
        raise ValueError("Every packaged workflow must be stopped.")
    references = customizations.findall("./connectionreferences/connectionreference")
    if (len(references) != (4 if role == "reviewer" else 6)
            or any(row.findtext("connectionid") not in (None, "") for row in references)):
        raise ValueError("All native connection references must be present and unbound.")
    logical_references = {row.get("connectionreferencelogicalname") for row in references}
    variables = {}
    for name, value in members.items():
        if name.startswith("environmentvariabledefinitions/") and name.endswith(".xml"):
            variable = ET.fromstring(value)
            schema = variable.get("schemaname")
            if (not schema or schema in variables or variable.tag != "environmentvariabledefinition"
                    or variable.findtext("defaultvalue") not in (None, "")
                    or variable.findtext("type") != "100000000"):
                raise ValueError("Native target configuration must use unique, unconfigured String definitions.")
            variables[schema] = variable
        if "environmentvariablevalue" in name.lower():
            raise ValueError("Target environment-variable current values cannot ship in the solutions.")
    if len(variables) != (8 if role == "reviewer" else 23):
        raise ValueError("The complete native configuration definitions must be retained.")
    workflows = {
        name: json.loads(value, object_pairs_hook=unique_object)
        for name, value in members.items()
        if name.startswith("Workflows/") and name.endswith(".json")
    }
    counts = []
    for workflow in workflows.values():
        properties = workflow["properties"]
        definition = properties["definition"]
        actions = flatten(definition["actions"])
        counts.append(len(actions))
        expected_mode = "invoker" if len(actions) == 225 else "embedded"
        for ref in properties["connectionReferences"].values():
            if ref.get("runtimeSource") != expected_mode:
                raise ValueError("Caller Invoker and owner/service Embedded boundaries must remain intact.")
            connection = ref.get("connection", {})
            if set(connection) != {"connectionReferenceLogicalName"}:
                raise ValueError("Flows must use native references without packaged connection instances.")
            if connection["connectionReferenceLogicalName"] not in logical_references:
                raise ValueError("A workflow connection reference is missing its native definition.")
        for name, parameter in definition.get("parameters", {}).items():
            if name.startswith("psr_"):
                if (name not in variables or parameter.get("type") != "String"
                        or parameter.get("metadata", {}).get("schemaName") != name
                        or parameter.get("defaultValue") != ""):
                    raise ValueError("A native flow parameter must resolve to its unconfigured definition.")
        if role == "automation":
            latch = definition.get("parameters", {}).get("psrDeploymentReady")
            if latch != {"type": "Bool", "defaultValue": False}:
                raise ValueError("Automatic deployment readiness must remain false.")
        if "PSR_PRESENTATION_READER_V4_3" in json.dumps(definition):
            populate = [action for action in actions
                        if isinstance(action.get("inputs"), dict)
                        and action["inputs"].get("host", {}).get("operationId") == "CreateFileItem"]
            if len(populate) != 1 or {
                    key for key in populate[0]["inputs"]["parameters"]
                    if key.startswith("dynamicFileSchema/")} != WORD_SCHEMA_KEYS:
                raise ValueError("The complete native Word action must retain four concrete schema roots.")
    if sorted(counts) != ACTION_COUNTS[role]:
        raise ValueError("The import-first package must retain every implemented workflow action.")
    components = [name for name in members if name.startswith("botcomponents/") and name.endswith("/data")]
    if len(components) != (19 if role == "reviewer" else 0):
        raise ValueError("Unexpected agent component closure.")
    if role == "reviewer":
        config = json.loads(members["bots/psr_PowerPlatformSolutionReviewer/configuration.json"])
        if config.get("publishOnImport") is not False:
            raise ValueError("Agent publication on import is forbidden.")
    return members


def verify(site=SITE, required=False, publication=False):
    site = Path(site)
    path = site / MANIFEST
    if not path.exists():
        if required:
            raise ValueError("The import-first release manifest is required.")
        return None
    release = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if (type(release.get("schemaVersion")) is not int or release["schemaVersion"] != 1
            or release.get("kind") != "IMPORT_FIRST_UNMANAGED_SOLUTION_RELEASE"
            or release.get("version") != VERSION
            or type(release.get("approvedPublicDistribution")) is not bool
            or set(release.get("files", {})) != set(PATHS)):
        raise ValueError("Invalid import-first release declaration.")
    if publication and release["approvedPublicDistribution"] is not True:
        raise ValueError("Parent safety approval is required before publishing new solution downloads.")
    expected_evidence = {
        "automaticWordRuntimeVerified": False,
        "crossTenantInstallationVerified": False,
        "separateLeastPrivilegeRequesterVerified": False,
        "publishedDemoAgentChanged": False,
        "setupOrActivationPerformed": False,
    }
    evidence = release.get("evidence", {})
    if (set(evidence) != {*expected_evidence, "sameTenantSandboxImportVerified"}
            or any(evidence.get(key) is not value for key, value in expected_evidence.items())
            or type(evidence.get("sameTenantSandboxImportVerified")) is not bool):
        raise ValueError("Import acceptance must not be represented as Word runtime acceptance.")
    contents = {}
    for role, expected_path in PATHS.items():
        row = release["files"][role]
        if (set(row) != {"path", "bytes", "sha256"} or row["path"] != expected_path
                or type(row["bytes"]) is not int or row["bytes"] <= 0
                or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise ValueError("Invalid same-origin download declaration: " + role)
        value = (site / expected_path).read_bytes()
        if len(value) != row["bytes"] or sha(value) != row["sha256"]:
            raise ValueError("Import-first download hash mismatch: " + role)
        contents[role] = value
    expected_members = {}
    for role in ("reviewer", "automation", "support"):
        members = (verify_solution(contents[role], role) if role != "support"
                   else archive_members(contents[role]))
        expected_members[role] = {
            name: {"bytes": len(value), "sha256": sha(value)} for name, value in members.items()
        }
    if release.get("archiveMembers") != expected_members:
        raise ValueError("Incomplete or stale import-first archive-member inventory.")
    occurrences = identifier_members(contents, paths=PATHS, roles=PATHS)
    identifiers = sorted({value for values in occurrences.values() for value in values})
    if (release.get("structuralIdentifierMembers") != occurrences
            or release.get("structuralIdentifiers") != identifiers):
        raise ValueError("Structural identifiers must have exact import-release member contexts.")
    imports = release.get("nativeImports", [])
    if not isinstance(imports, list) or any(
            not isinstance(row, dict) or set(row) != {"role", "status", "sha256", *NATIVE_CHECKS}
            for row in imports):
        raise ValueError("Native receipts must contain only sanitized exact-definition acceptance fields.")
    if evidence["sameTenantSandboxImportVerified"]:
        if (len(imports) != 2 or {row.get("role") for row in imports} != {"reviewer", "automation"}
                or any(row.get("status") != "Succeeded"
                       or any(row.get(check) is not True for check in NATIVE_CHECKS)
                       or row.get("sha256") != release["files"][row["role"]]["sha256"]
                       for row in imports)):
            raise ValueError("Native import evidence must bind both exact ZIPs and their verified definitions and state.")
    elif imports:
        raise ValueError("Unverified import receipts cannot be published as successful acceptance.")
    if publication and evidence["sameTenantSandboxImportVerified"] is not True:
        raise ValueError("Native import and exact definition verification are required before publication.")
    return release


def public_paths(site=SITE):
    return [MANIFEST, *PATHS.values()] if (Path(site) / MANIFEST).is_file() else []


def summary(release):
    return {
        "manifestPath": MANIFEST, "version": release["version"],
        "files": release["files"], "evidence": release["evidence"],
        "approvedPublicDistribution": release["approvedPublicDistribution"],
    }


def card(release):
    files = release["files"]
    native = ("Both exact ZIPs imported in one same-tenant sandbox with unchanged workflow definitions, "
              "flows stopped and the agent unpublished."
              if release["evidence"]["sameTenantSandboxImportVerified"]
              else "Native import of these candidate ZIPs has not been verified.")
    return f'''<article class="card" id="solution-download">
<span class="tag">Unmanaged solutions &middot; import, then configure</span>
<h3>Import the actual reviewer and automation.</h3>
<p>These are separate Power Platform solution ZIPs, not an outer bundle or
substitution templates. Import the reviewer first, then automation, with activation
disabled. Both retain their complete implementation; setup does not enable intake or email.</p>
<div class="actions"><a class="button primary" href="{files["reviewer"]["path"]}" download>1. Reviewer solution {VERSION}</a>
<a class="button primary" href="{files["automation"]["path"]}" download>2. Automation solution {VERSION}</a>
<a class="button secondary" href="{files["setup"]["path"]}">Import and setup instructions</a>
<a class="button secondary" href="{files["support"]["path"]}" download>Setup resources (not a solution)</a></div>
<p><strong>Import is not activation.</strong> Configure your own approved connections,
private storage, authentication and exact Word template/schema afterward. Publication,
manual enablement, authorized smoke checks and automatic intake acceptance are separate steps.</p>
<p class="fine-print">{html.escape(native)} No target setup, automatic Word run,
cross-tenant installation or separate least-privilege requester test is established.</p>
<details><summary>Download integrity and acceptance boundaries</summary>
<p><a href="{MANIFEST}">Exact solution/member hashes and import evidence</a></p>
<p class="fine-print">Reviewer SHA-256</p><code class="word-checksum">{files["reviewer"]["sha256"]}</code>
<p class="fine-print">Automation SHA-256</p><code class="word-checksum">{files["automation"]["sha256"]}</code>
</details></article>'''


def setup_section(release):
    instructions = release["files"]["setup"]["path"]
    return f'''<section class="section setup-section" id="setup" aria-labelledby="setup-title">
<div class="wrap"><div class="section-heading"><p class="eyebrow">04 / Import and setup</p>
<h2 id="setup-title">Import first.<br>Enable deliberately.</h2>
<p>A solution import installs components, not working connections, private SharePoint
resources or a OneDrive template. It is not permission to run the agent or automation.</p></div>
<div class="notice"><strong>Import the reviewer, then automation, with activation disabled.</strong>
<a href="{instructions}">Follow the complete import, setup and troubleshooting instructions.</a>
Do not overwrite an existing installation or import the supplementary setup archive as a solution.</div>
<ol class="setup-steps">
<li><h3>Approve and check a clean target</h3><p>Use an explicitly authorized nonproduction
Dataverse environment. Check existing component collisions, licensing, capacity, model
availability and DLP. Never rely on an implicit CLI environment or overwrite unrelated components.</p></li>
<li><h3>Import both actual solution ZIPs</h3><p>Import reviewer first, then automation.
Leave plugin/flow activation off and do not publish the agent. Verify all components,
connection references and native configuration definitions. Stop on missing dependencies,
unexpected activation or a binding requirement outside your authorization.</p></li>
<li><h3>Verify the owner and configure connections</h3><p>Bind your own approved SharePoint,
OneDrive for Business, Office 365 Users, Microsoft Copilot Studio, Office 365 Outlook and
Word Online (Business) connections. Preserve the manual collector's <strong>Invoker</strong>
identity and separate verified owner/service output connections. No maker fallback.</p></li>
<li><h3>Configure private resources and authentication</h3><p>Use the post-import setup
contract to verify imported ownership, the owner's physical default drive, private storage,
jobs/control schemas and native configuration. Never adopt unrelated resources or broaden
permissions to make setup pass. Reconfigure authenticated agent access and verify its model.</p></li>
<li id="word-template-setup"><h3>Verify the exact Word template and schema</h3><p>Upload the
unchanged included template only with authorization. Discover its real drive/file and
Word control schema; a mismatch is a stop, not permission to remove Word output.
Reports stay beneath Results in a solution-filename folder, with requester Read on the
report item only. Source and audit permissions do not broaden.</p></li>
<li><h3>Accept before explicit publication or enablement</h3><p>Setup finishes stopped,
unpublished and without source authorization. Separately approve publication/manual
enablement and harmless no-email smoke checks. Automatic intake needs exact-source/version
authorization and full report, coverage, privacy and Word-output acceptance. Email is
a further explicit authorization, never an installation side effect.</p></li></ol>
<div class="config-strip"><div><span>Flow default</span><strong>Stopped</strong></div>
<div><span>Control default</span><strong>Disabled / no email</strong></div>
<div><span>Agent default</span><strong>Unpublished</strong></div>
<div><span>Credentials shipped</span><strong>None</strong></div></div>
<p class="fine-print">Native import acceptance is separate from setup, target Word-schema
compatibility, runtime correctness and cross-tenant verification. Local setup tooling is
not a hosted Python service.</p></div></section>'''
