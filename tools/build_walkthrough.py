"""Validate reviewed matched-run inputs; render lossless presentation derivatives only."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import struct
import zlib

from prepare_real_example import render_text

SITE = Path(__file__).resolve().parents[1]
PREFIX = "examples/walkthrough-325"
PROVENANCE = PREFIX + "/provenance.json"
MARKDOWN = PREFIX + "/complete-review.md"
READER = "walkthrough.html"
IMAGE_ROLES = {
    "uploadMenu": "native-upload-menu.png",
    "uploadedRow": "native-upload-confirmed.png",
    "flowRun": "native-flow-run.png",
    "agentHandoff": "native-agent-handoff.png",
    "mainOpening": "native-main-opening.png",
    "component": "native-component.png",
    "email": "native-email-received.png",
    "mainAssessments": "native-main-assessments.png",
    "mainVerification": "native-main-verification.png",
}
PASS_IDS = ("C1", "C2", "C3", "C4", "C5")
BASE_REPORTS = {"MAIN.txt": "main", "inventory.json": "inventory", "coverage.json": "coverage"}
TOP_KEYS = {
    "schemaVersion", "kind", "approvedPublicDerivatives", "sourceDisplayName", "revision",
    "outcome", "accepted", "selected", "unavailable", "acceptedPassIds",
    "logicalAgentInvocations", "mainValid", "screenLinesSupplied", "totalScreenLines",
    "latestScreenCitation", "allFiveSelectedSourcesComplete", "email", "images", "reports",
}
EMAIL_KEYS = {
    "nativeSendStatus", "ownerInboxReceiptVerified", "expectedReportLinkVerified",
    "forwardedCorporateReceiptVerified", "controlsRestored",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError("Walkthrough input: " + message)


def json_value(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key.")
            result[key] = value
        return result
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique)


def number(value, minimum, maximum, name):
    require(type(value) is int and minimum <= value <= maximum, name + " must be an actual bounded integer.")


def png_dimensions(data):
    """Only pixel-bearing PNG chunks are accepted; metadata/animation is not."""
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), "image must be a genuine PNG encoding.")
    offset, chunks, dimensions = 8, [], None
    while offset < len(data):
        require(offset + 12 <= len(data), "truncated PNG.")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + length
        require(end <= len(data), "truncated PNG chunk.")
        body = data[offset + 8:offset + 8 + length]
        require(kind in {b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND"}, "PNG metadata or non-pixel chunk is forbidden.")
        require(zlib.crc32(kind + body) & 0xffffffff == struct.unpack(">I", data[end - 4:end])[0], "PNG CRC differs.")
        if kind == b"IHDR":
            require(not chunks and length == 13, "invalid PNG header.")
            dimensions = struct.unpack(">II", body[:8])
            require(all(0 < size <= 20000 for size in dimensions), "invalid PNG dimensions.")
        chunks.append(kind)
        offset = end
        if kind == b"IEND":
            require(length == 0 and end == len(data), "PNG trailing payload.")
            break
    require(dimensions and chunks.count(b"IHDR") == 1 and chunks[-1] == b"IEND" and b"IDAT" in chunks, "incomplete PNG.")
    return dimensions


def normalized_text(data):
    # This is HTML parser newline normalization, not a report-content rewrite.
    return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def verify(site=SITE):
    site = Path(site)
    location = site / PROVENANCE
    require(location.is_file(), "missing reviewed " + PROVENANCE + "; no predicted outcome or substitute images will be generated.")
    require(not location.is_symlink() and location.resolve().parent == (site.resolve() / PREFIX), "linked provenance or input directory is not permitted.")
    p = json_value(location.read_bytes())
    require(isinstance(p, dict) and set(p) == TOP_KEYS, "schemaVersion 1 keys differ; private IDs, links and extra fields are not permitted.")
    require(type(p["schemaVersion"]) is int and p["schemaVersion"] == 1, "schemaVersion must be 1.")
    require(p["kind"] == "REVIEWED_GENUINE_CANVAS_EMAIL_WALKTHROUGH", "wrong evidence kind.")
    for key in ["approvedPublicDerivatives", "mainValid", "allFiveSelectedSourcesComplete"]:
        require(p[key] is True, key + " must be explicitly true after review.")
    require(p["sourceDisplayName"] == "Data Entry Testing" and p["revision"] == "3.3.2.5", "source/revision is not the agreed genuine canvas export.")
    require(p["outcome"] == "ReviewPartial", "this contract requires the actual terminal ReviewPartial outcome, not a prediction.")
    number(p["selected"], 5, 5, "selected")
    number(p["accepted"], 3, 5, "accepted")
    number(p["unavailable"], 0, 2, "unavailable")
    require(p["accepted"] + p["unavailable"] == p["selected"], "accepted + unavailable must equal selected == 5.")
    ids = p["acceptedPassIds"]
    require(isinstance(ids, list) and all(isinstance(item, str) for item in ids), "acceptedPassIds must be a list of pass IDs.")
    require(len(ids) == len(set(ids)) == p["accepted"] and set(ids) <= set(PASS_IDS), "acceptedPassIds must match the actual accepted count.")
    require("C4" in ids, "the accepted screen walkthrough requires an accepted C4; do not substitute another image.")
    number(p["logicalAgentInvocations"], 1, 13, "logicalAgentInvocations")
    number(p["screenLinesSupplied"], 326, 326, "screenLinesSupplied")
    number(p["totalScreenLines"], 326, 326, "totalScreenLines")
    number(p["latestScreenCitation"], 1, p["screenLinesSupplied"], "latestScreenCitation")
    email = p["email"]
    require(isinstance(email, dict) and set(email) == EMAIL_KEYS, "email proof keys differ.")
    require(email["nativeSendStatus"] == "Succeeded", "native email did not succeed.")
    for key in ["ownerInboxReceiptVerified", "expectedReportLinkVerified", "controlsRestored"]:
        require(email[key] is True, "email." + key + " must be actually verified.")
    require(email["forwardedCorporateReceiptVerified"] is False, "corporate forwarding is not established by this proof contract.")
    expected_reports = dict(BASE_REPORTS, **{item + ".txt": "component" for item in ids})
    require(isinstance(p["images"], list) and isinstance(p["reports"], list), "images/reports must be arrays.")
    require(len(p["images"]) == len(IMAGE_ROLES) and len(p["reports"]) == len(expected_reports), "all nine images and every authoritative report are required.")
    seen = set()
    for group, expected in [("images", {file: role for role, file in IMAGE_ROLES.items()}), ("reports", expected_reports)]:
        for row in p[group]:
            keys = {"file", "role", "bytes", "sha256"} | ({"alt", "caption"} if group == "images" else set())
            require(isinstance(row, dict) and set(row) == keys, group + " record keys differ.")
            name = row["file"]
            require(isinstance(name, str) and name in expected and name not in seen, "unexpected, duplicate or unsafe file path.")
            seen.add(name)
            require(row["role"] == expected[name], "wrong file/role mapping.")
            number(row["bytes"], 1, 50 * 1024 * 1024, "bytes")
            require(isinstance(row["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "invalid SHA-256.")
            path = site / PREFIX / name
            require(path.is_file() and not path.is_symlink() and path.resolve().parent == location.parent.resolve(), "missing file or linked input: " + name)
            data = path.read_bytes()
            require(len(data) == row["bytes"] and sha(data) == row["sha256"], "reviewed byte/hash pin differs: " + name)
            if group == "images":
                png_dimensions(data)
                for key in ["alt", "caption"]:
                    text = row[key]
                    require(isinstance(text, str) and 10 <= len(text) <= 2000 and not re.search(r"[\x00-\x1f<>]", text), "plain, reviewed alt/caption text required.")
            else:
                value = data.decode("utf-8-sig")
                require(not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", value), "report contains non-display control characters.")
                if name.endswith(".json"):
                    require(isinstance(json_value(data), (dict, list)), "report appendix must be complete JSON.")
                if name == "MAIN.txt":
                    headings = re.findall(r"^(10|[1-9])\. [^\r\n]+", value, re.M)
                    require(headings == [str(i) for i in range(1, 11)], "complete MAIN must retain all ten ordered sections.")
    found = {item.name for item in location.parent.iterdir()}
    require(found <= seen | {"provenance.json", "complete-review.md"}, "unlisted walkthrough input; no raw originals/private review files may enter this directory.")
    return p


def documents(p):
    rows = {row["file"]: row for row in p["reports"]}
    order = ["MAIN.txt"] + [item + ".txt" for item in PASS_IDS if item in p["acceptedPassIds"]] + ["inventory.json", "coverage.json"]
    return [rows[name] for name in order]


def combined_target(p):
    start = (3 * p["totalScreenLines"]) // 4 + 1
    last_quarter = start <= p["latestScreenCitation"] <= p["totalScreenLines"]
    achieved = (
        p["accepted"] >= 4 and p["selected"] == 5 and p["mainValid"] is True
        and p["allFiveSelectedSourcesComplete"] is True and "C4" in p["acceptedPassIds"]
        and p["screenLinesSupplied"] == p["totalScreenLines"] and last_quarter
    )
    if achieved:
        summary = (
            f'Bounded combined target achieved in this ONE matched run: {p["accepted"]}/5 accepted, '
            'valid MAIN, all five selected original sources complete, and accepted C4 with a '
            f'last-quarter citation (line {p["latestScreenCitation"]} of {p["totalScreenLines"]}; '
            f'the last quarter starts at line {start}).'
        )
    else:
        summary = (
            'The bounded combined target is not established for this matched run. It requires '
            'at least 4/5 accepted, valid MAIN, all five selected original sources complete, '
            'and accepted C4 with full screen input and a last-quarter citation '
            f'(line {start} or later of {p["totalScreenLines"]}).'
        )
    summary += ' This does not demonstrate repeated at-least-4/5 performance or 90% reliability across different exports.'
    return {"achieved": achieved, "scope": "ONE_MATCHED_RUN_ONLY",
            "lastQuarterStartLine": start, "summary": summary}


def primary_content(p):
    return {
        "kind": p["kind"], "approvedPublicDerivatives": p["approvedPublicDerivatives"],
        "pagePath": READER, "provenancePath": PROVENANCE, "markdownPath": MARKDOWN,
        "mainPath": PREFIX + "/MAIN.txt",
        **{key: p[key] for key in ["sourceDisplayName", "revision", "outcome", "accepted", "selected", "unavailable", "acceptedPassIds",
                                 "logicalAgentInvocations", "mainValid", "screenLinesSupplied", "totalScreenLines", "latestScreenCitation",
                                 "allFiveSelectedSourcesComplete", "email"]},
        "briefCaveat": f'ReviewPartial: {p["accepted"]}/5 assessments accepted, {p["unavailable"]} unavailable; 326/326 screen lines supplied. Owner Inbox receipt and the matching protected-report link verified. Not an app pass rate.',
        "mainMethod": "Deterministic assembly of native-flow-accepted canonical AI component records; no new inference or regrading.",
        "combinedTarget": combined_target(p),
    }


def markdown(p, site=SITE):
    parts = [
        "# Complete matched canvas review\n\n",
        f'{p["sourceDisplayName"]} · revision {p["revision"]} · {p["outcome"]} · {p["accepted"]}/5 accepted.\n\n',
        "Presentation-only full derivative, not new findings or another assessment. "
        "Authoritative TXT/JSON bytes remain unchanged. Every complete source below includes "
        "its original content, unavailable records, omissions and footer where present. "
        "Input completeness does not prove every line was semantically examined; "
        "checker, compilation, import and runtime/accessibility execution were NOT RUN. "
        "Browser Print / Save as PDF is presentation only; no automated Word/PDF service is implemented.\n\n",
        "## Bounded combined target\n\n" + combined_target(p)["summary"] + "\n\n",
    ]
    for row in documents(p):
        value = (Path(site) / PREFIX / row["file"]).read_bytes().decode("utf-8")
        fence = "`" * max(3, 1 + max((len(run) for run in re.findall(r"`+", value)), default=0))
        separator = not value.endswith("\n")
        metadata = {key: row[key] for key in ["file", "bytes", "sha256"]}
        metadata["separatorAdded"] = separator
        parts.extend([
            f'## {row["file"]} · complete {row["role"]}\n\n',
            f'Authoritative source: [{row["file"]}]({row["file"]})\n\n',
            "<!-- complete-source " + json.dumps(metadata, separators=(",", ":")) + " -->\n",
            fence + ("json" if row["file"].endswith(".json") else "text") + "\n",
            value, "\n" if separator else "", fence + "\n\n",
        ])
    return "".join(parts)


def extract_markdown(value):
    """Recover original UTF-8 bytes, including BOM/CRLF and missing final newline."""
    result = {}
    pattern = re.compile(r"<!-- complete-source (\{[^\n]+\}) -->\n(`{3,})(?:text|json)\n")
    cursor = 0
    while match := pattern.search(value, cursor):
        meta = json.loads(match.group(1))
        end = value.find("\n" + match.group(2) + "\n", match.end())
        require(end >= 0, "Markdown closing fence missing.")
        body = value[match.end():end + 1]
        if meta["separatorAdded"]:
            body = body[:-1]
        data = body.encode("utf-8")
        require(len(data) == meta["bytes"] and sha(data) == meta["sha256"], "Markdown is not lossless.")
        require(meta["file"] not in result, "duplicate Markdown source.")
        result[meta["file"]] = data
        cursor = end + len(match.group(2)) + 2
    return result


def reader(p, site=SITE):
    site = Path(site)
    index = (site / "index.html").read_text(encoding="utf-8")
    script = re.search(r"<script>(.*?)</script>", index, re.S).group(1)
    style = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    light = re.search(r":root\s*\{(.*?)\}", style, re.S).group(1)
    sections, navigation, main_nav = [], [], []
    for row in documents(p):
        name, role = row["file"], row["role"]
        identifier = "main" if role == "main" else Path(name).stem.lower()
        value = normalized_text((site / PREFIX / name).read_bytes())
        title = {"main": "MAIN · all ten sections and full footer", "component": Path(name).stem + " · full accepted canonical assessment",
                 "inventory": "Complete inventory", "coverage": "Complete coverage and omissions"}[role]
        tree = " tree-text" if role in {"inventory", "coverage"} else ""
        navigation.append(f'<li><a href="#{identifier}">{html.escape(title)}</a></li>')
        sections.append(f'<section class="example-document" id="{identifier}" aria-labelledby="{identifier}-title"><header class="document-header"><div><p class="eyebrow">Complete reviewed authoritative file</p><h2 id="{identifier}-title">{html.escape(title)}</h2></div><a class="small-button" href="{PREFIX}/{name}" download>Download {Path(name).suffix} ↓</a></header><p class="document-pin">{row["bytes"]:,} bytes · SHA-256 <code>{row["sha256"]}</code></p><div class="report-text{tree}" data-walkthrough-text="{name}">{render_text(value, role)}</div></section>')
        if role == "main":
            main_nav = [f'<li><a href="#main-section-{number}">{html.escape(title)}</a></li>'
                        for number, title in re.findall(r"^\ufeff?(10|[1-9])\. ([^\n]+)", value, re.M)]
    accepted = ", ".join(p["acceptedPassIds"])
    unavailable = ", ".join(item for item in PASS_IDS if item not in p["acceptedPassIds"]) or "none selected"
    target = combined_target(p)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="referrer" content="no-referrer">
<script>{script}</script><title>Matched canvas walkthrough · complete {p["accepted"]}/5 review</title><style>{style}
@media print {{ :root, html[data-theme="dark"] {{{light}}} }}</style><link rel="stylesheet" href="site.css"><link rel="stylesheet" href="example.css"><script src="example.js" defer></script></head>
<body class="example-reader"><a class="skip-link" href="#main">Skip to the complete MAIN report</a><header class="site-header"><a class="brand" href="index.html#showcase"><span class="brand-mark" aria-hidden="true">[r]</span><span>Solution Reviewer<small>Matched improved-run report</small></span></a><nav aria-label="Reader navigation"><a href="index.html#showcase">Screenshot journey</a><a href="index.html#history">Historical evidence</a><a href="index.html#report-formats">Word / PDF options</a></nav><button id="theme-toggle" class="theme-button" type="button">Change theme</button></header>
<main class="wrap"><section class="example-intro"><p class="eyebrow">Data Entry Testing · genuine original canvas solution · revision {p["revision"]}</p><h1>The full matched report.<br><span>Partial, not an app verdict.</span></h1>
<p class="example-lead">{p["accepted"]}/5 selected-source assessments accepted; {p["unavailable"]} unavailable. This is the same native upload, review job, saved output and verified owner Inbox email shown in the primary walkthrough—not either earlier no-email benchmark.</p>
<div class="actions reader-actions"><a class="button primary" href="#main-section-1">Read the full MAIN ↓</a><a class="button secondary" href="{MARKDOWN}" download>Full report (.md) ↓</a><a class="button secondary" href="{PREFIX}/MAIN.txt" download>Authoritative MAIN (.txt) ↓</a><button class="button secondary" id="print-example" hidden type="button">Print / Save as PDF</button></div>
<div class="example-facts"><div><strong>{p["accepted"]} / 5</strong><span>accepted · {p["unavailable"]} unavailable, not an app pass rate</span></div><div><strong>326 / 326</strong><span>screen lines supplied · not exhaustive semantic examination</span></div><div><strong>{p["logicalAgentInvocations"]}</strong><span>logical agent invocations, not internal model inference count</span></div><div><strong>Verified</strong><span>owner Inbox receipt and matching protected-report link</span></div></div>
<p class="example-boundary" id="combined-target" data-combined-target-met="{str(target["achieved"]).lower()}">{html.escape(target["summary"])}</p>
<p class="example-boundary"><strong>AI component assessments; deterministic MAIN assembly.</strong> Complete accepted canonical records ({accepted}), unavailable records ({unavailable}), findings, strengths, checks, inventory, omissions and footer are retained. MAIN is not another AI inference, repair or regrade. All five selected original files were acquired completely; latest accepted screen citation: line {p["latestScreenCitation"]}. This does not prove each supplied line was semantically examined or that the whole app was assessed.</p>
<p class="example-boundary"><strong>Verification remains NOT RUN.</strong> No current checker, compilation, source-app/role/workflow import or runtime/accessibility execution occurred. Unavailable assessments are validation outcomes, not confirmed app defects. Retained syntax/default/fallback wording is not compiler or runtime proof.</p>
<p class="example-boundary"><strong>Matched delivery, bounded proof.</strong> Native SendEmailV2 succeeded; owner Inbox receipt and the expected protected-report link were verified. Existing forwarding keeps the original mailbox copy; forwarded corporate receipt is not established. Controls were restored. No mailbox settings changed, no Cc/Bcc or mail retry, and no exactly-once or all-client delivery guarantee is claimed.</p>
<p class="fine-print">All authoritative TXT/JSON files below are byte-identical to reviewed inputs. Privacy labels and masked links are not original source literals or live links. The Markdown download includes every full file, not a summary or new assessment. This historical run did not produce Word; <a href="index.html#word-output">the new Word output and solution bundle</a> have separate proof. Browser Print / Save as PDF is presentation only; automated PDF output is not implemented. <a href="{PROVENANCE}">Reviewed public derivative hashes</a>.</p></section>
<div class="report-layout"><aside class="example-toc" aria-label="Complete matched report contents"><p class="eyebrow">All authoritative documents</p><ol>{''.join(navigation)}</ol><details open><summary>All ten MAIN sections</summary><ol class="main-section-links">{''.join(main_nav)}</ol></details><p class="fine-print">No substitute unavailable component reports are invented. Complete content works without JavaScript.</p></aside><div class="report-documents">{''.join(sections)}</div></div></main>
<footer class="wrap site-footer"><p><strong>Matched genuine canvas review · {p["outcome"]}</strong><br>Source advice, not whole-app certification.</p><p><a href="index.html#showcase">Back to the screenshot journey</a> · <a href="follow-up.html">Separate no-email benchmarks</a></p></footer></body></html>'''


def verify_outputs(p, site=SITE):
    site = Path(site)
    expected = markdown(p, site)
    require((site / MARKDOWN).is_file() and (site / MARKDOWN).read_bytes() == expected.encode("utf-8"), "full Markdown is missing or stale; run build_walkthrough.py.")
    recovered = extract_markdown(expected)
    require(recovered == {row["file"]: (site / PREFIX / row["file"]).read_bytes() for row in documents(p)}, "Markdown source closure differs.")
    require((site / READER).is_file() and (site / READER).read_bytes() == reader(p, site).encode("utf-8"), "HTML reader is missing or stale; run build_walkthrough.py.")
    return recovered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        p = verify()
        if not args.verify_only:
            (SITE / MARKDOWN).write_bytes(markdown(p).encode("utf-8"))
            (SITE / READER).write_bytes(reader(p).encode("utf-8"))
        verify_outputs(p)
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(str(error)) from error
    print("Matched-run inputs verified; complete Markdown/TXT roundtrip and HTML generation verified. No new approval, runtime or publication action.")


if __name__ == "__main__":
    main()
