"""Prepare only the approved real-canvas derivatives; preserve all four TXT files."""
import argparse
import hashlib
import html
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

SITE = Path(__file__).resolve().parents[1]
PREFIX = "examples/real-canvas"
MANIFEST = "downloads/real-canvas-example-manifest.json"
BUNDLE = "downloads/real-canvas-review-example.zip"
ADDENDUM = "user-capture-provenance.v1.json"
ADDENDUM_PIN = "f3cb2bc2c68c078d7f314267d018878cef5b48d84f442c4241478c8092c98476"
PROVENANCE_PIN = "79b2cf94ba22bc4dda99229da77e8506af45506fefb74288a40e4372a22a2a92"
TEXT_PINS = {
    "real-canvas-MAIN.txt": "fa6e929b395b090041cbec0924a61b4fecb977ecc5bfe5211df02c28b0d19b8b",
    "real-canvas-C4.txt": "50d74ad328a2266823bb16266d60b5a5bee3df58badfae708440a3ceb6ddb69c",
    "real-canvas-inventory.txt": "4f02bf984b5a3c749408cade4b1ef4f46d35640b92cf3694fc3a91c27c7bacd4",
    "real-canvas-coverage.txt": "26dca2c3b5e299bbcfaa75382f84a9b2bccf54cffb0c53d0ed916bd38006e27e",
}
DOCUMENTS = [
    ("real-canvas-MAIN.txt", "main", "MAIN · all ten sections, footer and unavailable records"),
    ("real-canvas-C4.txt", "component", "C4 · complete accepted screen assessment"),
    ("real-canvas-inventory.txt", "inventory", "Complete retained inventory"),
    ("real-canvas-coverage.txt", "coverage", "Complete retained coverage · no fields omitted"),
    ("public-provenance.json", "provenance", "Native-capture and report provenance"),
    (ADDENDUM, "user-provenance", "User-provided capture provenance and correlation limits"),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def intake(directory):
    if (SITE / PREFIX).exists() or (SITE / MANIFEST).exists():
        raise ValueError("Existing integration must be verified, not overwritten by a new intake.")
    raw_addendum = (directory / ADDENDUM).read_bytes()
    if sha(raw_addendum) != ADDENDUM_PIN:
        raise ValueError("Approved addendum pin mismatch.")
    addendum = json.loads(raw_addendum.decode("utf-8-sig"))
    rows = addendum["screenshots"] + addendum["unchangedPriorPublicCandidates"]
    if len(rows) != 13 or len({row["file"] for row in rows}) != 13:
        raise ValueError("Exactly thirteen payload pins are required.")
    inputs = {ADDENDUM: raw_addendum}
    for row in rows:
        name = row["file"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("Only the approved leaf filenames are accepted.")
        data = (directory / name).read_bytes()
        if len(data) != row["bytes"] or sha(data) != row["sha256"]:
            raise ValueError("Approved payload pin mismatch: " + name)
        inputs[name] = data
    if sha(inputs["public-provenance.json"]) != PROVENANCE_PIN:
        raise ValueError("Approved original provenance differs.")
    if {p.name for p in directory.iterdir()} != set(inputs):
        raise ValueError("Input directory differs from the exact fourteen-file approval.")
    payloads = dict(inputs)
    approval = {
        "scope": "Parent-approved public derivatives of this exact real canvas review; not production, compiler, complete-application or runtime certification.",
        "parentReview": "Parent read complete redacted MAIN and both provenance records, verified fourteen pins and performed scoped restricted-context/private-binding/URL/email/credential screening with zero matches.",
        "siteReview": "Normal derivative visual/privacy review of the eight approved images. Site author did not inspect private originals or independently repeat the original-to-derivative pixel comparison.",
        "bodyPolicy": "All four TXT files, including BOM, complete coverage, claims, quotes, redactions and footer/unavailable records, remain byte-identical to the approved inputs.",
        "imagePolicy": "All eight image payloads remain byte-identical. Four user-provided images are not TEST captures; their capture times remain unknown.",
        "deliveryBoundary": "One guarded SendEmailV2 succeeded. Original owner Inbox receipt and recipient containment remain unverified after observed forwarding/autoreply. The user-provided notification body is not proof of verified Inbox receipt or single delivery.",
        "hostingBoundary": "Public derivative approval is distinct from hosting/deployment; hosting state is recorded separately in content.json.",
    }
    original = json.loads(inputs["public-provenance.json"].decode("utf-8-sig"))
    original["status"] = "PARENT_APPROVED_PUBLIC_REAL_CANVAS_DERIVATIVE_NOT_RUNTIME_ACCEPTANCE"
    original["visualQa"] = "TEST_REPORTED_DERIVATIVE_PRIVACY_PASS_PARENT_APPROVED_SITE_VISUAL_REVIEW_COMPLETED"
    original["publicApproval"] = approval
    original["inputProvenanceSha256"] = PROVENANCE_PIN
    payloads["public-provenance.json"] = (json.dumps(original, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    addendum["status"] = "PARENT_APPROVED_PUBLIC_USER_CAPTURE_DERIVATIVES_NOT_INBOX_RECEIPT_PROOF"
    addendum["publicApproval"] = True
    addendum["inputPublishedState"] = addendum.pop("published")
    addendum["originalCandidatePins"] = addendum.pop("unchangedPriorPublicCandidates")
    addendum["visualPrivacyQa"] = "TEST_REPORTED_DERIVATIVE_PRIVACY_PASS_PARENT_APPROVED_SITE_VISUAL_REVIEW_COMPLETED"
    addendum["publicDerivativeApproval"] = approval
    addendum["inputProvenanceSha256"] = ADDENDUM_PIN
    addendum["originalQaFieldScope"] = "Per-image QA strings describe the original TEST curation stage; the current parent public-derivative approval is recorded above. No capture origin, time, correlation or report claim is changed."
    addendum["publishedPayloadPins"] = [
        {"file": name, "sha256": sha(data), "bytes": len(data)}
        for name, data in payloads.items() if name != ADDENDUM
    ]
    payloads[ADDENDUM] = (json.dumps(addendum, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    for name, pin in TEXT_PINS.items():
        if sha(payloads[name]) != pin:
            raise ValueError("An approved TXT body was changed.")
    (SITE / PREFIX).mkdir(parents=True)
    records = []
    for name, data in payloads.items():
        (SITE / PREFIX / name).write_bytes(data)
        records.append({
            "path": PREFIX + "/" + name, "archivePath": name,
            "inputSha256": sha(inputs[name]), "inputBytes": len(inputs[name]),
            "sha256": sha(data), "bytes": len(data),
            "transformation": "Provenance approval/header and published-hash framing only" if name.endswith(".json") else "NONE_BYTE_IDENTICAL",
        })
    return {
        "schemaVersion": "1.0", "approvedPublicDerivatives": True,
        "scope": "REAL_CANVAS_REVIEW_PARTIAL_NOT_COMPLETE_APPLICATION_ASSESSMENT",
        "inputApprovalPins": {ADDENDUM: ADDENDUM_PIN, "public-provenance.json": PROVENANCE_PIN},
        "textBodyPins": TEXT_PINS, "files": records,
        "bundle": {"path": BUNDLE, "memberCount": 14},
        "outcome": "Partial: one of five assessments accepted, four unavailable; six model calls. C4 covers 80/326 screen lines.",
        "delivery": approval["deliveryBoundary"],
        "excluded": "No raw app/solution, private originals/diagnostics, mailbox/autoreply images, installer or previously excluded application material.",
        "archiveTimestamps": "Fixed to 1980 for reproducibility; not review or screenshot capture times.",
    }


def validate_files(m):
    if not m["approvedPublicDerivatives"] or m["textBodyPins"] != TEXT_PINS or len(m["files"]) != 14:
        raise ValueError("Real-example approval/pin structure differs.")
    for row in m["files"]:
        if row["path"] != PREFIX + "/" + row["archivePath"] or Path(row["archivePath"]).name != row["archivePath"]:
            raise ValueError("Unexpected public example path.")
        data = (SITE / row["path"]).read_bytes()
        if sha(data) != row["sha256"] or len(data) != row["bytes"]:
            raise ValueError("Published real-example file pin mismatch.")
        if row["archivePath"] in TEXT_PINS and sha(data) != TEXT_PINS[row["archivePath"]]:
            raise ValueError("An approved complete TXT file changed.")
        if row["archivePath"].endswith(".png") and row["sha256"] != row["inputSha256"]:
            raise ValueError("An approved image changed.")


def bundle_bytes(m):
    output = io.BytesIO()
    with ZipFile(output, "w") as archive:
        for row in m["files"]:
            info = ZipInfo(row["archivePath"], (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (SITE / row["path"]).read_bytes())
    return output.getvalue()


def render_text(value, kind):
    parts, pending = [], []
    headings = {"Component assessment", "Not assessed:", "Evidence-grounded findings", "Observed strengths", "Verification and not-assessed checks"}
    def flush():
        if pending:
            # An initial element prevents HTML's removal of a leading newline in pre.
            parts.append('<pre><span aria-hidden="true"></span>' + html.escape("".join(pending), quote=False) + "</pre>")
            pending.clear()
    for line in value.splitlines(keepends=True):
        match = re.match(r"^\ufeff?(10|[1-9])\. ", line) if kind == "main" else None
        if match or (kind == "component" and line.rstrip("\n") in headings):
            flush()
            identifier = ' id="main-section-' + match.group(1) + '"' if match else ""
            parts.append("<h3" + identifier + ">" + html.escape(line, quote=False) + "</h3>")
        else:
            pending.append(line)
    flush()
    return "".join(parts)


def reader(m):
    index = (SITE / "index.html").read_text(encoding="utf-8")
    script = re.search(r"<script>(.*?)</script>", index, re.S).group(1)
    style = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    light = re.search(r":root\s*\{(.*?)\}", style, re.S).group(1)
    pins = {row["archivePath"]: row for row in m["files"]}
    sections, navigation, main_nav = [], [], []
    for name, kind, title in DOCUMENTS:
        row = pins[name]
        value = (SITE / row["path"]).read_bytes().decode("utf-8-sig")
        tree = " tree-text" if kind in {"inventory", "coverage", "provenance", "user-provenance"} else ""
        sections.append(f'<section class="example-document" id="{kind}" aria-labelledby="{kind}-title"><header class="document-header"><div><p class="eyebrow">Complete published file</p><h2 id="{kind}-title">{html.escape(title)}</h2></div><a class="small-button" href="{row["path"]}" download>Download {Path(name).suffix} ↓</a></header><p class="document-pin">{row["bytes"]:,} bytes · SHA-256 <code>{row["sha256"]}</code></p><div class="report-text{tree}" data-example-text="{kind}">{render_text(value,kind)}</div></section>')
        navigation.append(f'<li><a href="#{kind}">{html.escape(title)}</a></li>')
        if kind == "main":
            main_nav = [f'<li><a href="#main-section-{number}">{html.escape(title)}</a></li>' for number, title in re.findall(r"^(10|[1-9])\. (.+)$", value, re.M)]
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Historical real canvas review · original 1/5 Partial</title>
<script>{script}</script><style>{style}
@media print {{ :root, html[data-theme="dark"] {{{light}}} }}</style>
<link rel="stylesheet" href="site.css"><link rel="stylesheet" href="example.css"><script src="example.js" defer></script></head>
<body class="example-reader"><a class="skip-link" href="#main">Skip to the complete MAIN report</a><header class="site-header"><a class="brand" href="index.html#showcase"><span class="brand-mark" aria-hidden="true">[r]</span><span>Solution Reviewer<small>Actual real-canvas review</small></span></a><nav aria-label="Reader navigation"><a href="index.html#showcase">Actual journey</a><a href="index.html#boundaries">Evidence boundaries</a><a href="index.html#report-formats">Word / PDF options</a></nav><button id="theme-toggle" class="theme-button" type="button">Change theme</button></header>
<main class="wrap"><section class="example-intro"><p class="eyebrow">Historical original 1/5 review · not the improved matched email walkthrough</p><h1>The original available record.<br><span>A historical Partial assessment.</span></h1><p class="example-boundary"><a href="walkthrough.html">Read the current matched improved-run report →</a> · <a href="index.html#history">Historical evidence context</a>. The original report, image and provenance bytes below are unchanged.</p>
<p class="example-lead">All ten MAIN sections and footer, the sole accepted C4 report, complete inventory and complete coverage. Four unavailable assessments are not fabricated or filled in.</p>
<div class="actions reader-actions"><a class="button primary" href="#main-section-1">Read the MAIN assessment ↓</a><a class="button secondary" href="{PREFIX}/real-canvas-MAIN.txt" download>Complete MAIN (.txt) ↓</a><a class="button secondary" href="{BUNDLE}" download>All 14 files (.zip) ↓</a><button class="button secondary" id="print-example" hidden type="button">Print / Save as PDF</button></div>
<div class="example-facts"><div><strong>1 / 5</strong><span>selected assessments accepted · four unavailable</span></div><div><strong>80 / 326</strong><span>screen lines covered by accepted C4</span></div><div><strong>6</strong><span>actual model calls · not phase-record count</span></div><div><strong>Partial</strong><span>not full application assessment</span></div></div>
<p class="example-boundary"><strong>Complete files ≠ complete coverage.</strong> Roles/customization and large data-source material were omitted or outside scope. Three embedded checker records have unknown age; no current checker ran. Retained “syntactically valid” wording is not compiler or Power Fx semantic-parser proof. No source application, roles or workflow were imported or executed.</p>
<p class="example-boundary"><strong>Notification is not verified Inbox receipt.</strong> One guarded SendEmailV2 succeeded. Original owner Inbox receipt and recipient containment remain unverified after observed forwarding/autoreply. The user-provided body image shows no mailbox/recipient headers and does not guarantee single delivery.</p>
<p class="fine-print">All four TXT payloads are byte-identical to the approved redacted inputs, including the complete 58,939-byte coverage file. Bracketed privacy labels are not original source literals or working links. Existing replacement characters/wording are retained, not silently corrected. Every file below is visible and printable without JavaScript.</p>
<p class="fine-print">ZIP SHA-256: <code class="example-bundle-sha">{m["bundle"]["sha256"]}</code> · <a href="{MANIFEST}">Input/published pins and exact archive manifest</a>. The ZIP contains reports, eight approved images and two provenance records—not the app or an installer.</p>
<p class="fine-print">Current report output is TXT/JSON. This static reader and browser Print / Save as PDF are presentation options, not a deployed document-generation flow. <a href="index.html#report-formats">Optional protected Word/PDF guidance</a>.</p></section>
<div class="report-layout"><aside class="example-toc" aria-label="Complete record contents"><p class="eyebrow">Read every available file</p><ol>{''.join(navigation)}</ol><details open><summary>MAIN sections</summary><ol class="main-section-links">{''.join(main_nav)}</ol></details><p class="fine-print">C1/C2/C3/C5 are unavailable. Their records remain in MAIN and coverage; no report is invented.</p></aside><div class="report-documents">{''.join(sections)}</div></div></main>
<footer class="wrap site-footer"><p><strong>Actual real-canvas review · Partial</strong><br>Source-backed advice, not runtime certification.</p><p><a href="index.html#showcase">Back to the actual journey</a> · <a href="{MANIFEST}">Verify complete-file hashes</a></p></footer></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-directory", type=Path)
    args = parser.parse_args()
    m = intake(args.input_directory) if args.input_directory else json.loads((SITE / MANIFEST).read_text(encoding="utf-8"))
    validate_files(m)
    data = bundle_bytes(m)
    if "sha256" in m["bundle"] and sha(data) != m["bundle"]["sha256"]:
        raise ValueError("Approved real-example archive changed.")
    m["bundle"].update(sha256=sha(data), bytes=len(data))
    (SITE / "downloads").mkdir(exist_ok=True)
    (SITE / BUNDLE).write_bytes(data)
    (SITE / MANIFEST).write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (SITE / "full-example.html").write_text(reader(m), encoding="utf-8", newline="")
    print("Real-example files verified: four TXT bodies and eight images unchanged.")
    print("Complete 14-file archive SHA-256:", m["bundle"]["sha256"])


if __name__ == "__main__":
    main()
