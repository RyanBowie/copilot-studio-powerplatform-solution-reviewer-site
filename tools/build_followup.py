"""Publish only reviewed derivative bytes and render their complete escaped text."""

import argparse
import hashlib
import html
import json
from pathlib import Path
import re

from prepare_real_example import render_text

SITE = Path(__file__).resolve().parents[1]
PREFIX = "examples/follow-up"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def intake(source):
    source = source.resolve()
    if not source.is_relative_to(SITE / "_private-hold"):
        raise ValueError("Only reviewed private staging is an intake source.")
    audit = json.loads((source / "private-redaction-audit.json").read_text(encoding="utf-8"))
    body = (source / "complete-review.txt").read_bytes()
    metrics = (source / "results.json").read_bytes()
    if (audit["manualContentReviewComplete"] is not True
            or audit["publicDerivativeSha256"] != sha(body)
            or audit["publicDerivativeBytes"] != len(body)):
        raise ValueError("The complete report differs from its content/privacy review.")
    target = SITE / PREFIX
    if target.exists():
        raise ValueError("Existing public follow-up inputs cannot be overwritten.")
    target.mkdir(parents=True)
    (target / "complete-review.txt").write_bytes(body)
    (target / "results.json").write_bytes(metrics)
    provenance = {
        "kind": "REVIEWED_GENUINE_CANVAS_FOLLOW_UP_DERIVATIVE",
        "approvedPublicDerivative": True,
        "completeAssembledMain": True,
        "allTenSectionsAndFooterRetained": True,
        "redactionBoundary": "Private source identities, links, schema/table names and connection references are masked. Labels are not original source literals. No original package or private source fingerprint is published.",
        "reportBoundary": "AI-generated component assessments passed the existing flow checks. MAIN is deterministic report assembly, not a second AI assessment or a corrected failed narrative. Report wording is retained, not compiler proof.",
        "newScreenshotsIncluded": False,
        "files": [
            {"path": PREFIX + "/complete-review.txt", "bytes": len(body), "sha256": sha(body)},
            {"path": PREFIX + "/results.json", "bytes": len(metrics), "sha256": sha(metrics)},
        ],
    }
    (target / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


def verify():
    provenance = json.loads((SITE / PREFIX / "provenance.json").read_text(encoding="utf-8"))
    if provenance["approvedPublicDerivative"] is not True or provenance["completeAssembledMain"] is not True:
        raise ValueError("The public report review is missing.")
    for row in provenance["files"]:
        if row["path"] not in (PREFIX + "/complete-review.txt", PREFIX + "/results.json"):
            raise ValueError("Unexpected follow-up publication input.")
        data = (SITE / row["path"]).read_bytes()
        if sha(data) != row["sha256"] or len(data) != row["bytes"]:
            raise ValueError("A reviewed follow-up file changed.")
    return provenance


def coverage_section():
    verify()
    data = json.loads((SITE / PREFIX / "results.json").read_text(encoding="utf-8"))
    latest = data["latest"]
    repeat = [row for row in data["comparisons"] if row["revision"] == latest["revision"]]
    if len(repeat) != 2 or any(row["accepted"] != 3 or row["mainValid"] is not True for row in repeat):
        raise ValueError("This public explanation requires the two reviewed 3/5, valid-MAIN measurements.")
    rows = []
    for row in data["comparisons"]:
        screen = ("Full source; cited line " + str(row["latestAcceptedScreenCitation"])) if row["screenAccepted"] else "No accepted screen"
        rows.append("<tr><td>" + html.escape(row["revision"]) + " / " + html.escape(row["attempt"])
                    + f'</td><td>{row["accepted"]}/5</td><td>{"Valid" if row["mainValid"] else "Invalid"}</td>'
                    + f'<td>{html.escape(screen)}</td><td>{row["logicalAgentInvocations"]}</td></tr>')
    return f'''<section class="section wrap" id="coverage-improvements" aria-labelledby="coverage-plan-title">
<div class="section-heading"><p class="eyebrow">Separate no-email benchmarks · historical comparisons</p><h2 id="coverage-plan-title">Two earlier repeat runs.<br>All 11 follow-ups retained.</h2><p>These benchmarks are distinct from the new matched email walkthrough above. Revision 3.3.2.5 improved from the historical <strong>1/5 to 3/5 accepted assessments</strong>, with valid MAIN in both unchanged-revision benchmark runs. That is 60% rather than 20%—more accepted than unavailable. It is <strong>not an app pass rate</strong>, and the original 4/5 target remained unmet in these two benchmarks.</p></div>
<div class="snapshot-metrics follow-up-metrics"><div class="metric"><strong>3 / 5</strong><span>accepted in each of two repeat runs</span></div><div class="metric"><strong>326 / 326</strong><span>screen content lines supplied to an accepted assessment</span></div><div class="metric"><strong>2 / 2</strong><span>valid assembled MAIN reports</span></div></div>
<div class="actions"><a class="button secondary" href="follow-up.html">Read the separate benchmark MAIN →</a><a class="button secondary" href="{PREFIX}/complete-review.txt" download>Benchmark MAIN (.txt) ↓</a><a class="button secondary" href="{PREFIX}/results.json">All 11 historical results</a></div>
<div class="two-up">
<article class="card"><h3>What is working better.</h3><p>All five original selected files were supplied completely. The accepted screen assessment now receives all 326 content lines, not just the first 80, with source-backed citations through line 285 in both repeat runs. Source acquisition and citation bounds now agree.</p><p>Complete input does not prove every line was semantically examined. This remains five selected sources, not every file in the solution.</p></article>
<article class="card"><h3>AI assessments, deterministic MAIN.</h3><p>The primary standard-harness agent creates the component assessments. Only accepted canonical records enter the ten-section MAIN assembler. MAIN now retains their complete observations, findings, strengths, checks and unavailable records without another model rewriting or regrading them.</p><p>These runs used 7 and 9 logical agent invocations respectively; MAIN assembly is not another MAIN model inference. GPT-5 Chat is configured. GPT-5 Reasoning is not required.</p></article>
<article class="card"><h3>Two assessments remain unavailable.</h3><p>The solution manifest, app YAML and screen YAML were accepted in both repeats. The embedded checker and workflow assessments were rejected: quote-length and serialized-value evidence problems remain. Invalid responses were not relabeled successful.</p><p>Exact evidence, response-shape, privacy and stop checks remain in place. No current checker, compilation, source import or runtime/accessibility execution occurred. Email stayed OFF.</p></article>
<article class="card"><h3>Targets at the historical benchmark stage.</h3><p><strong>At least 4/5 plus valid MAIN:</strong> not achieved together in these two historical no-email benchmark runs. Earlier experiments reached 4/5 but failed MAIN. This is not a verdict on the new matched walkthrough; its bounded combined-target result is reported separately above. <strong>At least 90% across a declared repeated export set:</strong> not demonstrated; these two runs use the same single genuine export.</p><p>Larger-file handling, control-aware chunking and reliable original-path mapping remain further work. Failed and unsupported sources stay visible. Complete-source acquisition is not whole-app certification.</p></article>
</div>
<details><summary>All 11 measured follow-ups, including regressions</summary><div class="details-body"><p>Every row is a completed original-byte comparison against the same five selected sources. Attempt identifiers are retained; one earlier upload was interrupted before a review job and is not counted as an assessment run. Revision 3.3.1.8 had no genuine comparison.</p><div style="overflow-x:auto"><table><thead><tr><th>Revision / attempt</th><th>Accepted</th><th>MAIN</th><th>Accepted screen evidence</th><th>Agent invocations</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p>The historical 3.3.1.3 example remains 1/5, valid MAIN, 80/326 screen lines and six invocations. Native generation experiments regressed to 0/5; those failures are retained, not hidden behind the latest result.</p></div></details>
<p class="notice">These two benchmark runs had email OFF; they are not the primary matched upload/email walkthrough and do not supply its screenshots or email proof. The original four TXT reports, eight historical images and exact 14-file bundle remain unchanged. No installable package or cross-tenant certification is claimed.</p>
</section>'''


def reader():
    provenance = verify()
    metrics = json.loads((SITE / PREFIX / "results.json").read_text(encoding="utf-8"))
    latest = metrics["latest"]
    value = (SITE / PREFIX / "complete-review.txt").read_bytes().decode("utf-8")
    index = (SITE / "index.html").read_text(encoding="utf-8")
    script = re.search(r"<script>(.*?)</script>", index, re.S).group(1)
    style = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    light = re.search(r":root\s*\{(.*?)\}", style, re.S).group(1)
    row = provenance["files"][0]
    navigation = "".join(
        f'<li><a href="#main-section-{number}">{html.escape(title)}</a></li>'
        for number, title in re.findall(r"^(10|[1-9])\. (.+)$", value, re.M)
    )
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Measured follow-up · Complete canonical MAIN</title>
<script>{script}</script><style>{style}
@media print {{ :root, html[data-theme="dark"] {{{light}}} }}</style>
<link rel="stylesheet" href="site.css"><link rel="stylesheet" href="example.css"><script src="example.js" defer></script></head>
<body class="example-reader"><a class="skip-link" href="#main">Skip to the complete MAIN report</a>
<header class="site-header"><a class="brand" href="index.html#showcase"><span class="brand-mark" aria-hidden="true">[r]</span><span>Solution Reviewer<small>Measured genuine follow-up</small></span></a><nav aria-label="Reader navigation"><a href="index.html#coverage-improvements">Measured results</a><a href="full-example.html">Historical example</a><a href="index.html#report-formats">Word / PDF options</a></nav><button id="theme-toggle" class="theme-button" type="button">Change theme</button></header>
<main class="wrap"><section class="example-intro"><p class="eyebrow">Historical no-email benchmark · not the matched email walkthrough</p><h1>Complete source supplied.<br><span>Partial assessment retained.</span></h1>
<p class="example-lead">Revision {html.escape(latest["revision"])} accepted {latest["accepted"]}/5 selected-source assessments, with a valid assembled MAIN. Both unchanged-revision benchmark runs accepted 3/5. The 4/5 combined target remained unmet in these two historical no-email benchmark runs, not a verdict on the new matched walkthrough.</p>
<div class="actions reader-actions"><a class="button primary" href="#main-section-1">Read the complete MAIN ↓</a><a class="button secondary" href="{PREFIX}/complete-review.txt" download>Complete MAIN (.txt) ↓</a><button class="button secondary" id="print-example" hidden type="button">Print / Save as PDF</button></div>
<div class="example-facts"><div><strong>{latest["accepted"]} / 5</strong><span>accepted · two unavailable</span></div><div><strong>326 / 326</strong><span>screen content lines supplied to an accepted assessment</span></div><div><strong>{latest["logicalAgentInvocations"]}</strong><span>logical agent invocations in this run</span></div><div><strong>Partial</strong><span>not whole-app certification</span></div></div>
<p class="example-boundary"><strong>AI assessments; deterministic MAIN assembly.</strong> All supplied canonical observations, findings, strengths, verification items, unavailable records, inventory and omissions are retained below. MAIN does not invent or regrade findings and is not a second AI assessment.</p>
<p class="example-boundary"><strong>Not exhaustive semantic coverage.</strong> Full source was supplied; this does not prove every line was examined. The denominator is five selected files, not the whole solution. SARIF and workflow assessments remained unavailable. No current checker, compilation, import or runtime/accessibility tests ran. Retained syntax/default/fallback wording is not compiler or runtime proof.</p>
<p class="fine-print">This is the complete redacted assembled MAIN, including its footer. All canonical records supplied to MAIN are included; private links to separate original artifacts are masked, not public downloads. The complete original export and protected diagnostics are not published. Historical images and email evidence are unchanged; email was OFF for these follow-ups.</p>
<p class="fine-print">These historical runs used TXT/JSON, not Word. <a href="index.html#word-output">The new Word output and solution bundle</a> have separate proof. Browser Print / Save as PDF is a presentation option; automated PDF output is not implemented. <a href="{PREFIX}/provenance.json">Reviewed public-file hashes</a> · <a href="{PREFIX}/results.json">Every measured comparison</a>.</p></section>
<div class="report-layout"><aside class="example-toc" aria-label="Complete report contents"><p class="eyebrow">All ten MAIN sections</p><details open><summary>MAIN sections</summary><ol class="main-section-links">{navigation}</ol></details></aside><div class="report-documents"><section class="example-document" id="main" aria-labelledby="main-title"><header class="document-header"><div><p class="eyebrow">Complete reviewed public derivative</p><h2 id="main-title">Assembled MAIN and full footer</h2></div><a class="small-button" href="{PREFIX}/complete-review.txt" download>Download TXT ↓</a></header><p class="document-pin">{row["bytes"]:,} bytes · SHA-256 <code>{row["sha256"]}</code></p><div class="report-text" data-followup-text>{render_text(value, "main")}</div></section></div></div></main>
<footer class="wrap site-footer"><p><strong>Measured improvement, not complete success.</strong><br>Same-source repetition is not broad-export reliability.</p><p><a href="index.html#coverage-improvements">Back to the full comparison</a></p></footer></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-input", type=Path)
    args = parser.parse_args()
    if args.approved_input:
        intake(args.approved_input)
    (SITE / "follow-up.html").write_text(reader(), encoding="utf-8", newline="")
    print("Complete reviewed follow-up rendered; private evidence and identities were not copied.")


if __name__ == "__main__":
    main()
