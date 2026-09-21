"""Build the primary page only from the reviewed matched email-walkthrough contract."""
import html
import json
from pathlib import Path
import re

from build_followup import coverage_section
from build_walkthrough import SITE, PREFIX, PROVENANCE, MARKDOWN, PASS_IDS, verify, png_dimensions, primary_content, combined_target
from word_release import verify as verify_word_release, section as word_section, formats_section, PATHS
from solution_release import verify as verify_solutions, setup_section as import_setup_section


def build(p, site=SITE):
    site = Path(site)
    old = (site / "index.html").read_text(encoding="utf-8")
    head = old.split("<body>")[0]
    head = re.sub(r"<title>.*?</title>", f'<title>Matched {p["accepted"]}/5 canvas review · Power Platform Solution Reviewer</title>', head, flags=re.S)
    release = verify_word_release(site)
    solutions = verify_solutions(site)
    if release:
        head = re.sub(r"<title>.*?</title>", "<title>Word reports and solution download · Power Platform Solution Reviewer</title>", head, flags=re.S)

    def section(name):
        match = re.search(r'<section\b[^>]*\bid="' + name + r'"[^>]*>.*?</section>', old, re.S)
        if not match:
            raise ValueError("Missing retained generic section: " + name)
        return match.group()

    def figure(role, eager=False):
        row = next(row for row in p["images"] if row["role"] == role)
        path = PREFIX + "/" + row["file"]
        width, height = png_dimensions((site / path).read_bytes())
        loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
        alt = html.escape(row["alt"], quote=True)
        return f'<figure class="screenshot" data-image-role="{role}"><a class="image-link" href="{path}" aria-label="Inspect full-size reviewed native image: {alt}"><img src="{path}" width="{width}" height="{height}" alt="{alt}" {loading}></a><figcaption>{html.escape(row["caption"])}</figcaption></figure>'

    def stage(number, label, title, images, context, identifier=""):
        attr = f' id="{identifier}"' if identifier else ""
        return f'<article class="journey-stage"{attr}><div class="journey-heading"><span class="journey-number">{number:02}</span><div><p>{label}</p><h2>{title}</h2></div></div><div class="screenshot-stack">{images}</div><p class="journey-context">{context}</p></article>'

    accepted = ", ".join(p["acceptedPassIds"])
    unavailable = ", ".join(item for item in PASS_IDS if item not in p["acceptedPassIds"]) or "none selected"
    target = combined_target(p)
    component_text = "\n".join((site / PREFIX / row["file"]).read_text(encoding="utf-8-sig")
                               for row in p["reports"] if row["role"] == "component")
    review_scope = ""
    if all(term in component_text for term in (
            "NewForm", "SubmitForm", "DataCardValue1", "DataCardValue3", "MissingDependency")):
        review_scope = '''<section class="section wrap" id="review-scope"><div class="section-heading"><p class="eyebrow">What the recorded review actually recommends</p><h2>Source observations.<br>Concrete next checks.</h2></div><div class="two-up"><article class="card"><h3>Accessibility and dependencies</h3><p>The accepted checker assessment identifies historical accessible-label warnings for <code>DataCardValue1</code> and <code>DataCardValue3</code>, plus a readable-screen-name warning. It recommends checking their current state, not treating old checker results as confirmed current defects.</p><p>The screen assessment recommends verifying accessible names for NEW and SAVE and keyboard access to SAVE. The manifest assessment recommends resolving required connection references before an import.</p></article><article class="card"><h3>Power Fx: the current depth limit</h3><p>The screen assessment observes <code>NewForm</code> and <code>SubmitForm</code>, the form structure and a data table. This is a real bounded static review, but this example does not demonstrate comprehensive Power Fx correctness, formula rewrites, delegation analysis or application-error detection.</p><p>Error handling, effective accessibility and runtime behaviour still need verification. No new static defects were confirmed by these accepted assessments. Current App Checker, compilation and runtime tests: <strong>NOT RUN</strong>. Accepted evidence records are not a guarantee that every AI recommendation is semantically correct.</p></article></div><p><a href="walkthrough.html">Read the complete recommendations and their source evidence →</a></p></section>'''
    metrics = f'<div class="snapshot-metrics case-metrics"><div class="metric"><strong>{p["accepted"]} / 5</strong><span>assessments accepted · {p["unavailable"]} unavailable</span></div><div class="metric"><strong>326 / 326</strong><span>screen lines supplied, not proof each was examined</span></div><div class="metric"><strong>{p["logicalAgentInvocations"]}</strong><span>logical agent invocations, not internal inference count</span></div></div>'
    stages = [
        stage(1, "NATIVE UPLOAD", "Select → uploaded row", figure("uploadMenu", True) + figure("uploadedRow"),
              "The original Data Entry Testing classic canvas solution ZIP—not a code app or synthetic demo—was uploaded to approved private storage. The menu precedes selection; the row confirms the upload. This website accepts no uploads."),
        stage(2, "ACTUAL FLOW RUN", "New file → review job", figure("flowRun"),
              '<span id="automatic-intake"><strong>When a file is created (properties only)</strong> watches <code>SolutionPackages/Incoming</code>; polling is configured every minute, not instant delivery. <strong>A new file, not a new folder.</strong> Only eligible <code>.zip</code> / <code>.msapp</code> files directly in Incoming pass enabled-intake, approval and file-scope checks. Empty folders and files in new subfolders are outside scope. <strong>No chat prompt is needed.</strong></span>'),
        stage(3, "ACTUAL AGENT ACTION", "Evidence → assessment", figure("agentHandoff"),
              f'<span id="agent-handoff"><code>ExecuteCopilotAsyncV2</code> invokes the standard Copilot Studio agent with source evidence. This matched run used <strong>{p["logicalAgentInvocations"]} logical agent invocations</strong>, not that number of internal model inferences. All five selected original sources were acquired completely. The agent does not independently watch storage or execute the app.</span>'),
        stage(4, "SAVED MATCHED OUTPUT", "MAIN + accepted component", figure("mainOpening") + figure("component"),
              f'<strong>{p["accepted"]}/5 accepted: {accepted}.</strong> Unavailable: {unavailable}. MAIN deterministically assembles native-flow-accepted canonical AI component records, not another AI inference or regrade. Screen input is 326/326 lines; the latest accepted citation is line {p["latestScreenCitation"]}. These native views are excerpts, not the complete documents.'),
        stage(5, "VERIFIED OWNER INBOX", "Received email → report link", figure("email"),
              '<strong>Native SendEmailV2 succeeded; owner Inbox receipt and the matching protected-report link were verified.</strong> This is the same job as the upload and report—not an earlier benchmark or a notification preview. Forwarded corporate receipt is not established. <a href="#delivery-boundary">Exact delivery boundary</a>.'),
        stage(6, "NATIVE FULL REPORT VIEWS", "Open the full report", figure("mainAssessments") + figure("mainVerification"),
              '<a href="walkthrough.html">Open the complete matching report →</a> All ten MAIN sections, canonical records, unavailable assessments, omissions and the full footer are available in the reader and Markdown/TXT downloads. Screenshots are real native viewports; presentation order is not a claim of continuous capture or an unrecorded click.', "report-captures"),
    ]
    page = f'''<body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="brand" href="#top"><span class="brand-mark" aria-hidden="true">[r]</span><span>Solution Reviewer<small>Matched improved run · experimental</small></span></a><nav aria-label="Main navigation"><a href="#showcase">Screenshot journey</a><a href="#full-example">Full report</a><a href="#reference">Tools &amp; topics</a><a href="#setup">Setup</a><a href="#history">History</a></nav><button id="theme-toggle" class="theme-button" type="button">Change theme</button></header>
<main id="main"><section class="showcase wrap" id="showcase" aria-labelledby="top"><div class="showcase-intro"><div><p class="eyebrow">Data Entry Testing · {p["revision"]}</p><h1 id="top">A real upload.<br><span>A review you can inspect.</span></h1></div><div class="showcase-pitch"><p>Upload → flow → agent → report → received email. One matched native run.</p><div class="actions"><a class="button primary" data-full-example-link href="walkthrough.html">Read the full {p["accepted"]}/5 report →</a><a class="button secondary" href="{MARKDOWN}" download>Full Markdown ↓</a></div><p class="showcase-caution"><strong>{p["outcome"]} · {p["accepted"]}/5 accepted, {p["unavailable"]} unavailable.</strong> Not an app pass rate.</p></div></div>
<p class="journey-note"><strong>Nine reviewed native views of the same upload, review and received email.</strong> Captions retain capture order, crops and limits.</p>
<div class="screenshot-journey">{''.join(stages)}</div><p class="notice showcase-review-note"><span id="example-caveat">{html.escape(primary_content(p)["briefCaveat"])}</span> <a href="#coverage-improvements">Separate benchmarks and remaining targets →</a></p></section>
<section class="section full-example-section" id="full-example"><div class="wrap example-entry"><div><p class="eyebrow">Complete report from this exact walkthrough</p><h2>Every available record.<br>Not a whole-app verdict.</h2><p>The full MAIN, all {p["accepted"]} accepted canonical component reports, inventory and coverage are retained—not replaced by a short summary. All five selected original files were acquired completely; this is not evidence that every line was semantically examined.</p>{metrics}<p class="notice" id="combined-target" data-combined-target-met="{str(target["achieved"]).lower()}">{html.escape(target["summary"])}</p></div><div class="card example-access"><span class="tag">Matched {p["outcome"]} · verified owner Inbox receipt</span><h3>Read it. Download it. Print it.</h3><p>The full Markdown derivative preserves the complete authoritative TXT/JSON content. No new findings, source app, installer or private originals are included.</p><div class="actions"><a class="button primary" href="walkthrough.html">Open the full report reader →</a><a class="button secondary" href="{MARKDOWN}" download>Full report (.md) ↓</a></div><p><a href="{PREFIX}/MAIN.txt" download>Authoritative MAIN (.txt) ↓</a> · <a href="{PROVENANCE}">Matched evidence hashes</a></p><p class="fine-print">Current checker, compilation, import and runtime/accessibility execution: NOT RUN. Browser Print / Save as PDF is presentation only.</p></div></div></section>
<section class="section wrap"><details id="image-provenance"><summary>Matched capture origin, privacy and chronology</summary><div class="details-body"><p>All nine primary screenshots are reviewed public pixel derivatives of this genuine native upload/email walkthrough. Their exact filenames, roles, sizes, hashes and reviewed captions come from the matched provenance. Screenshots remain viewports; the complete report is separately readable.</p><p>Private IDs, tenant links, mailbox addresses and raw-source fingerprints are not public evidence. Capture chronology is limited to what the reviewed captions establish; the page does not invent a continuous recording or claim a click that was not captured.</p><p><a href="{PROVENANCE}">Matched-run provenance</a> · <a href="PRIVACY-REPORT.json">Independent hash-bound public screening</a></p></div></details></section>
'''
    boundaries = f'''<section class="section wrap" id="boundaries"><div class="section-heading"><p class="eyebrow">Evidence boundaries</p><h2>More accepted. Still bounded.</h2></div><div class="two-up">
<article class="card"><h3>Complete input is not complete assessment.</h3><p>{p["accepted"]}/5 selected-source assessments were accepted; {p["unavailable"]} remain unavailable. Accepted: {accepted}. Unavailable: {unavailable}. Failed validation is not an app defect. The earlier C2/C5 checker/workflow assessments were unavailable because of response/evidence-validation issues, not confirmed defects in the app.</p><p><a href="#combined-target">The bounded combined-target result above applies to this one matched run only.</a> At least 90% reliability across a declared repeated set of different exports remains unproven. <a href="#coverage-improvements">All 11 historical follow-ups and regressions</a> remain available.</p></article>
<article class="card"><h3>Report wording is not tool execution.</h3><p>All 326 screen lines were supplied; citation bounds do not prove every line was semantically examined. Five selected files are not the whole solution. Larger-file handling and original-path provenance remain limitations.</p><p>Retained syntax/default/fallback claims are not compilation or Power Fx semantic-parser proof. Embedded checker records are historical, not a new official checker run. Suggested verifications remain NOT RUN; no app, role or workflow import/execution or runtime/accessibility certification is implied.</p></article>
<article class="card" id="delivery-boundary"><h3>Received in the owner Inbox.</h3><p>Native <code>SendEmailV2</code> succeeded for the exact authorized source/version and verified demo owner. Owner Inbox receipt and the matching protected-report link were verified. No Cc/Bcc or email retry was used; controls were restored.</p><p>Existing forwarding keeps the original mailbox copy. Forwarded corporate receipt is not established; mailbox settings were not changed. No exactly-once, recipient-containment-beyond-this-proof or all-client rendering guarantee is made. The model cannot choose recipients.</p></article>
<article class="card" id="model-choice"><h3>Standard harness. GPT-5 Chat.</h3><p><strong>Revision 3.3.2.5 uses GPT5Chat; GPT-5 Reasoning is not required.</strong> Components are AI-generated; MAIN is deterministic assembly of native-flow-accepted canonical records, not a new inference or regrade. The harness is standard Copilot Studio, not GitHub Copilot.</p><p>Choose a supported available model and evaluate grounded quality, response reliability, latency and cost. No model choice establishes production readiness. Native flows/storage support this limited trusted-export pattern; no hosted Python/Azure worker or hardened hostile-archive handling is claimed.</p></article></div></section>'''
    history = '''<section class="section wrap" id="history"><div class="section-heading"><p class="eyebrow">Historical evidence · not the primary walkthrough</p><h2>The original record stays intact.</h2><p>The historical 1/5 screenshot run is preserved separately: four byte-identical TXT reports, eight unchanged images, two original public provenance records and the exact 14-file archive. Its 80/326-line screen prefix and unverified original Inbox receipt are historical limitations, not the measurements of the matched improved run above.</p></div><div class="actions"><a class="button secondary" href="full-example.html">Historical complete reader →</a><a class="button secondary" href="downloads/real-canvas-review-example.zip" download>Historical 14-file bundle ↓</a><a class="button secondary" href="downloads/real-canvas-example-manifest.json">Historical immutable hashes</a></div></section>'''
    reference = section("reference").replace("Example model · not required", "Current model · selectable").replace("PreviewModels / GPT5Reasoning", "GPT5Chat · revision 3.3.2.5")
    formats = section("report-formats").replace("TXT/JSON today.", "TXT/JSON authority. Full Markdown reader.")
    if "The complete Markdown and HTML reader" not in formats:
        formats = formats.replace("The reader supports browser Print / Save as PDF.", "The complete Markdown and HTML reader preserve authoritative TXT/JSON content. The reader supports browser Print / Save as PDF.")
    setup = section("setup")
    workflows = section("workflows")
    if release:
        page = page.replace(
            '<main id="main">',
            '<main id="main">' + word_section(release, hero=True, solutions=solutions),
            1,
        ).replace(
            '<h1 id="top">A real upload.<br><span>A review you can inspect.</span></h1>',
            '<h2 id="walkthrough-title">A real upload.<br><span>A review you can inspect.</span></h2>',
        ).replace(
            'id="showcase" aria-labelledby="top"', 'id="showcase" aria-labelledby="walkthrough-title"',
        ).replace(
            '<small>Matched improved run · experimental</small>', '<small>Word output · experimental</small>',
        ).replace(
            '<nav aria-label="Main navigation">',
            '<nav aria-label="Main navigation"><a href="#word-output">Word output</a><a href="#solution-download">Download</a>',
        ).replace('<a href="#full-example">Full report</a>', "")
        formats = formats_section()
        setup = setup.replace(
            '<strong>No installer is included in this public preview.</strong> The outline below is generic operator guidance. Obtain separately approved source and packages; target installation and activation require their own authorization and validation.',
            f'<strong>A configure-before-import Word solution bundle is included.</strong> <a href="{PATHS["setup"]}">Follow its complete setup instructions</a> to produce target-specific solution ZIPs. The outer bundle and unconfigured templates are not direct import inputs; no cross-tenant installation is claimed.',
        ).replace("Bind the five target connections", "Bind the six target connections").replace(
            "SharePoint, OneDrive for Business, Office 365 Users, Microsoft Copilot Studio and Office 365 Outlook.",
            "SharePoint, OneDrive for Business, Office 365 Users, Microsoft Copilot Studio, Office 365 Outlook and Word Online (Business).",
        )
        if 'id="word-template-setup"' not in setup:
            setup = setup.replace(
                "<li><h3>Configure and import the reviewer</h3>",
                f'<li id="word-template-setup"><h3>Upload and bind the Word template</h3><p>Use the exact <a href="{PATHS["template"]}">included template</a> in the configured output service user\'s supported template storage. Discover its actual file/drive and Word control schema; do not copy demo IDs or guess field keys. Configure the existing Results destination. Word reports use a solution-filename folder and report-item-only requester Read, not a separate private Word-output folder.</p></li><li><h3>Configure and import the reviewer</h3>',
            )
        if solutions:
            setup = import_setup_section(solutions)
        reference = reference.replace(
            "<strong>Actual registered tool:</strong>", "<strong>Evidence tool:</strong>",
        ).replace(
            "Rules 3.3.1 instruction text, pinned to its recorded publication.",
            "Word-enabled reviewer draft instruction reference, with target-specific bindings omitted.",
        ).replace(
            "Links do not grant access.",
            "Email links do not themselves grant access. Word delivery separately grants Read on the generated report before returning its link.",
        ).replace(
            "current collector evidence JSON → generated detailed interactive answer.",
            "current collector evidence JSON → finalized detailed review → formatted Word report and requester-accessible link.",
        ).replace(
            "COMPONENT passes then MAIN.", "AI COMPONENT passes, then deterministic MAIN assembly.",
        ).replace(
            "Leading <code>PSR_COMPONENT_INPUT_V3</code> or <code>PSR_REVIEW_ONLY_V1</code>.",
            "Leading <code>PSR_REVIEW_ONLY_V1</code>. Component assessment requests remain with the primary generative agent.",
        ).replace(
            "Supplied evidence text ≤60,100 characters. Prefixes route data; the external flow enforces identity.",
            "Supplied acquisition metadata and flow-accepted canonical component records, within the topic's current bounds. Prefixes are not authentication.",
        ).replace(
            "<code>ResponseContract</code> + <code>result</code>. COMPONENT → one <code>PSR_COMPONENT_V3</code> JSON object. MAIN → ten-section synthesis.",
            "Deterministic ten-section MAIN assembly. No new model generation or regrading of accepted component assessments in this topic.",
        )
        if 'id="word-format-topic"' not in reference:
            reference = reference.replace('<div class="topic-grid">', '''<div class="topic-grid">
<article class="card topic-card" id="word-format-topic"><p class="mono">topics\\FormatCurrentReviewPresentation.mcs.yml</p><h4>Format current review presentation</h4><dl><dt>Trigger</dt><dd>Internal Word-delivery route after the review is finalized; not a new assessment.</dd><dt>Inputs</dt><dd>The complete current review and its established context.</dd><dt>Output</dt><dd>Deterministic <code>PSR_PRESENTATION_READER_V4_3</code> presentation JSON for the supported Word controls.</dd><dt>Guards</dt><dd>Retains exact source meaning; the helper validates the model and source before creating the report. No model-selected recipients.</dd></dl></article>''', 1)
        for identifier, filename in (
                ("instructions-source", "agent-instructions.txt"),
                ("topics-source", "topic-tool-source.json")):
            text = (site / "reference" / filename).read_text(encoding="utf-8")
            reference, count = re.subn(
                r'(<(pre|code)\b[^>]*\bid="' + identifier + r'"[^>]*>).*?(</\2>)',
                lambda match: match[1] + html.escape(text) + match[3],
                reference, flags=re.S,
            )
            if count != 1:
                raise ValueError("Expected one complete no-JavaScript reference block: " + identifier)
        if 'id="word-tool-reference"' not in reference:
            reference = reference.replace("</tbody>", '''<tr id="word-tool-reference"><th scope="row">Existing reviewer Word tool</th><td><code>CreateCurrentReviewWord</code> / <code>InvokeFlowTaskAction</code>, called after the current review is finalized. The internal <code>FormatCurrentReviewPresentation</code> topic creates its deterministic presentation model.</td><td>Topic-only tool, exact-source validation, configured owner/service output connections. Source acquisition remains caller Invoker. No separate agent or new assessment.</td></tr>
<tr><th scope="row">Word Online (Business) and report delivery</th><td><code>CreateFileItem</code> populates the supported Word template; SharePoint saves the real DOCX, grants report-item Read to the established requester, and returns its URL.</td><td>Rebind the actual target template schema and connections. Unique report filenames preserve earlier runs. The public example proves one synthetic format-only run, not automatic Word delivery or target installation.</td></tr></tbody>''', 1)
        if 'id="word-workflow-extension"' not in workflows:
            workflows = workflows.replace("</section>", '<div class="wrap"><p class="notice" id="word-workflow-extension"><strong>Word-enabled delivery extension:</strong> finalized review &rarr; deterministic presentation &rarr; Word template &rarr; existing Results/solution-filename folder &rarr; requester report Read &rarr; usable link. The earlier real-solution screenshots are unchanged historical evidence; the new native Word proof is a separate synthetic test.</p></div></section>')
    footer = '''</main><footer class="wrap site-footer"><p><strong>Power Platform Solution Reviewer</strong><br>Experimental community PoC; no Microsoft endorsement.</p><p>No uploads, chat backend, telemetry or external fonts.<br><a href="README.md">Site notes</a> · <a href="#top">Back to top ↑</a></p><p id="hosting-note"></p></footer><dialog class="image-viewer" id="image-viewer" aria-labelledby="image-viewer-title"><div class="viewer-toolbar"><h2 id="image-viewer-title">Reviewed matched native image</h2><div><button class="small-button" id="viewer-zoom" type="button" aria-pressed="false">Actual size</button><button class="small-button" id="viewer-close" type="button" autofocus>Close ×</button></div></div><p class="caption" id="viewer-caption"></p><div class="viewer-canvas" id="viewer-canvas" tabindex="0" role="region" aria-label="Scrollable full-resolution reviewed image"></div><p class="caption">Unchanged reviewed derivative. <a id="viewer-file" download>Download full-size image</a></p></dialog><div id="copy-status" class="visually-hidden" role="status" aria-live="polite"></div></body></html>'''
    return head + page + review_scope + history + coverage_section() + formats + workflows + reference + setup + boundaries + footer


def main():
    try:
        p = verify()
        content = json.loads((SITE / "content.json").read_text(encoding="utf-8"))
        if content["example"] != primary_content(p):
            raise ValueError("Regenerate content.json/content.js from reviewed walkthrough inputs first.")
        (SITE / "index.html").write_bytes(build(p).encode("utf-8"))
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error
    print("Primary six-stage walkthrough uses only reviewed matched-run inputs; history remains separate.")


if __name__ == "__main__":
    main()
