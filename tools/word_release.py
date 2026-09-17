"""Verified public Word assets and a configure-before-import solution distribution."""
import hashlib
import base64
import html
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
from zipfile import ZipFile
from urllib.parse import unquote

SITE = Path(__file__).resolve().parents[1]
MANIFEST = "downloads/word-output-release.json"
VERSION = "3.3.2.6"
IMAGE_PREFIX = "examples/word-output"
IMAGE_NAMES = ["report-page-1.png", "report-page-2.png"]
PATHS = {
    "bundle": f"downloads/solution-reviewer-word-output-{VERSION}.bundle.zip",
    "template": "downloads/current-review-v4.3.1.web.template.docx",
    "setup": "downloads/WORD-OUTPUT-SETUP.md",
    "example": IMAGE_PREFIX + "/review-example.docx",
    "page1": IMAGE_PREFIX + "/" + IMAGE_NAMES[0],
    "page2": IMAGE_PREFIX + "/" + IMAGE_NAMES[1],
}
PUBLIC_PATHS = [MANIFEST, *PATHS.values()]
QA_SCOPE = "WORD_RELEASE_AND_MATCHED_WALKTHROUGH_LOCAL_QA"
PRIVACY_SCOPE = "WORD_RELEASE_AND_MATCHED_WALKTHROUGH_PUBLIC_TREE"
PUBLICATION_SCOPE = "WORD_RELEASE_AND_MATCHED_WALKTHROUGH_APPROVED_ASSETS"
GUID = re.compile(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", re.I)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate release JSON key: " + key)
        result[key] = value
    return result


def archive_members(data):
    with ZipFile(io.BytesIO(data)) as archive:
        rows = archive.infolist()
        names = [row.filename for row in rows]
        if len(names) != len({PurePosixPath(name).as_posix().casefold() for name in names}):
            raise ValueError("Duplicate archive members.")
        if sum(row.file_size for row in rows) > 50 * 1024 * 1024:
            raise ValueError("Public archive exceeds the expansion limit.")
        for row in rows:
            path = PurePosixPath(row.filename)
            if (path.is_absolute() or ".." in path.parts or "\\" in row.filename
                    or ":" in row.filename or any(part.endswith((" ", ".")) for part in path.parts)
                    or (row.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError("Unsafe archive member.")
        if archive.testzip() is not None:
            raise ValueError("Archive integrity check failed.")
        return {row.filename: archive.read(row.filename) for row in rows if not row.is_dir()}


def text_variants(value):
    variants = [value, unquote(value)]
    if "\\u" in value:
        variants.append(re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match.group(1), 16)), value))
    for candidate in re.findall(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{40,}={0,2}", value):
        if len(candidate) % 4 == 0:
            try:
                decoded = base64.b64decode(candidate, validate=True).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                continue
            if all(character.isprintable() or character in "\r\n\t" for character in decoded):
                variants.append(decoded)
    return variants


def identifier_members(contents):
    inventory = {}

    def inspect(label, data, depth=0):
        if depth > 4:
            raise ValueError("Unexpected identifier-inventory archive depth.")
        if label.lower().endswith((".zip", ".docx")):
            for name, value in archive_members(data).items():
                inspect(label + "::" + name, value, depth + 1)
        elif not label.lower().endswith(".png"):
            texts = text_variants(label + "\n" + data.decode("utf-8-sig"))
            identifiers = sorted({value.lower() for text in texts for value in GUID.findall(text)})
            if identifiers:
                inventory[label] = identifiers

    for role in ("bundle", "template", "example", "setup"):
        inspect(PATHS[role], contents[role])
    return inventory


def verify_docx(data):
    members = archive_members(data)
    if not {"[Content_Types].xml", "word/document.xml"} <= members.keys():
        raise ValueError("The Word download is not a DOCX package.")
    if any("vbaproject" in name.lower() or name.lower().endswith(".bin") for name in members):
        raise ValueError("Macro or embedded binary content is not approved for these Word examples.")
    return members


def verify_bundle(data, template):
    members = archive_members(data)
    required = [
        "psr_PowerPlatformSolutionReviewer.portable.template.zip",
        "psr_PowerPlatformSolutionAutomation.portable.template.zip",
        "install.py", "target.example.json", "install-manifest.json",
    ]
    for name in required:
        matches = [value for path, value in members.items() if PurePosixPath(path).name == name]
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous distribution member: " + name)
        if name.endswith(".zip"):
            solution = archive_members(matches[0])
            if not {"solution.xml", "customizations.xml"} <= solution.keys():
                raise ValueError("The distribution must contain real solution packages.")
            texts = b"\n".join(value for path, value in solution.items()
                               if path.endswith((".xml", ".json", ".yml", "/data")))
            if b"shared_wordonlinebusiness" not in texts or b"PSR_PRESENTATION_READER_V4_3" not in texts:
                raise ValueError("A solution package is missing the current Word-output integration.")
    if not any(value == template for path, value in members.items() if path.endswith(".docx")):
        raise ValueError("The bundle does not contain the exact public Word template.")
    return members


def verify(site=SITE, required=False):
    site = Path(site)
    manifest = site / MANIFEST
    if not manifest.exists():
        if required:
            raise ValueError("The reviewed Word release manifest is required.")
        return None
    data = json.loads(manifest.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if (type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1
            or data.get("kind") != "REVIEWED_WORD_OUTPUT_CONFIGURABLE_RELEASE"
            or data.get("distributionVersion") != VERSION
            or data.get("layoutVersion") != "4.3.1"
            or data.get("approvedPublicDerivatives") is not True):
        raise ValueError("Unsupported or unapproved public Word release.")
    expected_evidence = {
        "fixture": "synthetic", "formatOnlyRegeneration": True,
        "nativeGenerationVerified": True, "wordWebPages": 2, "desktopWordPages": 2,
        "reviewContentPreserved": True, "requesterReadGrantVerified": True,
        "separateLeastPrivilegeAccountTested": False,
        "publishedDemoAgentUpdated": False, "automaticWordRunVerified": False,
        "crossTenantInstallationVerified": False, "wordOutlineHeadings": False,
    }
    if (data.get("evidence") != expected_evidence
            or any(type(data["evidence"][key]) is not type(value) for key, value in expected_evidence.items())):
        raise ValueError("Word evidence must retain its exact tested scope and limitations.")
    if (data.get("packageKind") != "PORTABLE_DERIVED_CONFIGURE_BEFORE_IMPORT"
            or set(data.get("files", {})) != set(PATHS)):
        raise ValueError("A complete configure-before-import release is required.")
    contents = {}
    for role, expected in PATHS.items():
        row = data["files"][role]
        if (set(row) != {"path", "bytes", "sha256"} or row["path"] != expected
                or type(row["bytes"]) is not int or row["bytes"] <= 0
                or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise ValueError("Invalid public asset declaration: " + role)
        value = (site / expected).read_bytes()
        if len(value) != row["bytes"] or sha(value) != row["sha256"]:
            raise ValueError("Public Word asset differs from its reviewed pin: " + role)
        contents[role] = value
    verify_docx(contents["template"])
    verify_docx(contents["example"])
    members = verify_bundle(contents["bundle"], contents["template"])
    expected_members = {
        name: {"bytes": len(value), "sha256": sha(value)} for name, value in members.items()
    }
    if data.get("bundleMembers") != expected_members:
        raise ValueError("The distribution member manifest is incomplete or stale.")
    identifiers = data.get("structuralIdentifiers")
    if (not isinstance(identifiers, list) or len(identifiers) != len(set(identifiers))
            or any(not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", value)
                   for value in identifiers)):
        raise ValueError("Reviewed structural identifiers must be an explicit UUID inventory.")
    occurrences = identifier_members(contents)
    if (data.get("structuralIdentifierMembers") != occurrences
            or set(identifiers) != {value for values in occurrences.values() for value in values}):
        raise ValueError("Structural identifiers must match exact reviewed archive-member contexts.")
    for role in ("page1", "page2"):
        image = contents[role]
        if image[:8] != b"\x89PNG\r\n\x1a\n" or image[12:16] != b"IHDR":
            raise ValueError("Word page illustrations must be PNG.")
        width, height = struct.unpack(">II", image[16:24])
        if width < 400 or height < 400:
            raise ValueError("Word page illustration is too small to inspect.")
    return data


def summary(release):
    return {
        "manifestPath": MANIFEST, "distributionVersion": release["distributionVersion"],
        "layoutVersion": release["layoutVersion"], "files": release["files"],
        "evidence": release["evidence"], "packageKind": release["packageKind"],
    }


def section(release, hero=False):
    if release is None:
        return ""
    files = release["files"]
    figures = "".join(
        f'<figure class="word-page"><a href="{files[role]["path"]}" '
        f'aria-label="Inspect page {number} of the redacted Word example">'
        f'<img src="{files[role]["path"]}" alt="Page {number} of the privacy-redacted '
        f'synthetic review Word example" loading="lazy"></a>'
        f'<figcaption>Page {number} &middot; local rendering of the redacted Word derivative.</figcaption></figure>'
        for number, role in enumerate(("page1", "page2"), 1)
    )
    heading, identifier = ("h1", "top") if hero else ("h2", "word-title")
    return f'''<section class="section wrap word-release" id="word-output" aria-labelledby="{identifier}">
<div class="section-heading"><p class="eyebrow">New &middot; Word output and solution bundle {VERSION}</p>
<{heading} id="{identifier}">Readable Word reports.<br>The same solution reviewer.</{heading}>
<p>The existing reviewer can turn its completed assessment into a formatted <code>.docx</code>,
save it beneath <code>Results/solution-&lt;filename&gt;/</code>, and grant the established
requester Read access to that report. No separate agent or separate private Word-output store.</p></div>
<div class="two-up"><article class="card">
<span class="tag">Native Word delivery verified &middot; synthetic fixture</span>
<h3>Read the report, not formatting markers.</h3>
<p>The tested layout puts the summary and findings first, keeps supporting evidence nearby,
and retains nested relationships without large empty-control gaps.
The same completed test review rendered as <strong>two pages in Word for web and desktop Word</strong>.
Original TXT/JSON audits were retained; formatting did not reassess the package.</p>
<div class="actions"><a class="button primary" href="{files["example"]["path"]}" download>Download Word example (.docx)</a>
<a class="button secondary" href="{files["template"]["path"]}" download>Download Word template</a></div>
<p class="fine-print">The example is a privacy-redacted derivative of actual native output.
The images below render that derivative locally, not native browser screenshots.
This synthetic fixture is separate from the historical Data Entry Testing 4/5 walkthrough.</p>
</article><article class="card" id="solution-download">
<span class="tag">Configure before import &middot; derived distribution</span>
<h3>Install the Word-enabled components.</h3>
<p>The bundle contains reviewer and automation solution templates, the matching Word template,
target configuration tooling, connection settings and setup instructions. It is not a
ready-bound export of the demo tenant.</p>
<div class="actions"><a class="button primary" href="{files["bundle"]["path"]}" download>Download solution bundle {VERSION}</a>
<a class="button secondary" href="{files["setup"]["path"]}">Setup and release notes</a></div>
<p><strong>Configure and repack first.</strong> Do not import this outer bundle or the
unconfigured <code>*.portable.template.zip</code> files directly.</p>
<p class="fine-print">Word Online (Business) licensing and policy approval are required.
Rebind your own connections, output destination and the template's actual discovered schema.
Target installation and activation need their own validation.</p>
<details><summary>Download integrity</summary><p class="fine-print">Bundle SHA-256</p>
<code class="word-checksum">{html.escape(files["bundle"]["sha256"])}</code>
<p><a href="{MANIFEST}">All public asset and archive-member hashes</a></p></details>
</article></div>
<div class="word-pages two-up">{figures}</div>
<p class="notice" id="word-proof-boundary"><strong>What this establishes:</strong> native, format-only
Word generation and requester report access for one synthetic review. The requester was also
the existing site owner, not a separate least-privilege test account. The demo's existing
reviewer draft and helper were updated; its published agent and automatic flow were not
released with Word output. The automatic candidate is included in the derived bundle but
has no native Word-run acceptance. No cross-tenant installation, broad reliability,
source-app execution or production certification is claimed. Headings have visual formatting,
not Word Heading 1/outline semantics.</p></section>'''


def formats_section():
    return '''<section class="section wrap" id="report-formats">
<div class="section-heading"><p class="eyebrow">Report formats</p><h2>Word for reading.<br>Original evidence retained.</h2></div>
<div class="two-up"><article class="card"><h3>Native Word output</h3><p>Word Online (Business)
populates the supported template; SharePoint stores a new run-specific DOCX and grants the
verified requester Read on that report before returning its link. Source collection remains
caller Invoker; output connections use an explicitly configured owner/service identity.</p>
<p>The tested Word layout works in Word for web and desktop. It does not upgrade review
status, execute the app, invent findings, change email policy or expose the whole output folder.</p></article>
<article class="card"><h3>Audit and historical formats</h3><p>Complete original TXT/JSON audits remain
authoritative. The earlier real-solution walkthrough retains its full Markdown/HTML reader and
unchanged downloads; it is not retroactively relabeled as a Word run.</p><p>Browser Print /
Save as PDF remains a presentation option. Automated PDF output is <strong>not implemented</strong>.</p></article></div></section>'''
