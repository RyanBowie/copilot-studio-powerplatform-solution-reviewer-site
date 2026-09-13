# Solution Reviewer — actual real-canvas review walkthrough

Screenshot-first, static Clawpilot-themed public derivatives of one genuine
classic canvas solution review. **Not a synthetic example.** No upload/chat
backend, telemetry, remote fonts or tracking.

## Six-step automatic journey

1. Upload a trusted solution ZIP or canvas `.msapp` directly into Incoming.
2. SharePoint detects the new file and starts the Power Automate review flow.
   The configured **When a file is created (properties only)** trigger
   (`GetOnNewFileItems`) polls `SolutionPackages/Incoming` every minute; this
   is not an instant-delivery or latency guarantee. Enabled-intake, approval,
   privacy and file-scope checks gate processing. After bounded extraction,
   `ExecuteCopilotAsyncV2` supplies evidence to the published review agent
   without a chat prompt.
3. The agent reviews bounded evidence; six model calls occurred in this example.
4. Inspect the actual saved MAIN/C4 reports and explicit coverage limits.
5. View the guarded notification body and its protected-report link, with
   delivery limitations retained.
6. Open the full report: all three user-provided report screenshots show its
   opening/scope, assessment/findings, and verification/omissions. A link opens
   the complete redacted assessment, not just those viewport excerpts.

Steps 2–3 are **configuration explainers, not flow-run screenshots or synthetic
runs**. The agent does not independently monitor storage. Creating an empty
folder does not start a review; files inside newly created subfolders are also
outside the current direct-Incoming-file scope. This page change does not
enable intake, approve another upload or run the agent.
The report screenshots do not independently prove an email-link click.

## What the real run establishes

**Partial: one of five selected assessments accepted, four unavailable, six
actual model calls.** The complete available MAIN, sole accepted C4 assessment,
inventory and coverage are provided. C4 covers only **80 of 326 screen lines**.
Roles/customization and large data-source material are omitted or unassessed.
Complete files are not complete application assessment.

Three embedded checker records are historical with unknown age; no current
official checker ran. Retained “syntactically valid” wording is **not compilation
or Power Fx semantic-parser proof**. Suggestions remain NOT RUN; the app, roles
and workflow were not imported or executed. No production/runtime/accessibility/
security or cross-tenant certification is claimed.

[Complete readable/printable output](full-example.html) ·
[All 14 approved files](downloads/real-canvas-review-example.zip) ·
[Input/published hashes and exact archive manifest](downloads/real-canvas-example-manifest.json)

The four TXT files are byte-identical to the approved inputs, including BOM,
quotes, privacy labels, all ten MAIN sections/footer/unavailable records, and
the entire **58,939-byte coverage** appendix. Existing wording/replacement
characters are not silently corrected. The HTML reader escapes text rather
than interpreting report content as markup; all six text/provenance documents
are readable without JavaScript and included by browser Print / Save as PDF.

## Capture origin and delivery boundary

The leading journey uses actual native before-selection and confirmed-uploaded
row images, native MAIN/C4 views and the **user-provided notification-body image**.
The three further MAIN images were also supplied by the user—not captured by
Test. Their capture times are unknown; analysis timestamps are not capture times.
Correlation is limited exactly as the two provenance records describe.

**One guarded `SendEmailV2` succeeded, but original owner Inbox receipt and
recipient containment remain unverified after observed forwarding/autoreply.**
The notification body has no sender/recipient/mailbox/folder identity and is
not verified Inbox receipt or a single-delivery guarantee. Mixed Inbox/autoreply
images are excluded.

All eight images retain the exact approved derivative bytes. Test reports pixel
privacy review; the site author reviewed the approved derivatives visually and
with offline OCR, not private originals. Only provenance approval/header and
published-hash framing was updated. Report claims, source quotes and capture
correlations were not rewritten.

## Product reference and formatting options

The reviewer uses the standard Copilot Studio harness, not GitHub Copilot.
GPT-5 Reasoning is Preview and is not recommended for production.

Manual: consent topic → actual internal `CollectReviewEvidence` tool via
`InvokeFlowTaskAction` → caller-owned OneDrive **Invoker** → source advice.
Automation uses SharePoint file events, bounded native extraction, the same
agent through `ExecuteCopilotAsyncV2`, protected reports and separately guarded
`SendEmailV2`. Flow capabilities are not arbitrary model-controlled tools;
the model cannot choose recipients or sharing.

Current runtime report output is TXT/JSON. This static reader and browser
Print / Save as PDF are presentation options. Optional Word/PDF flow guidance
is **not implemented or included**: a controlled template, private resources,
explicit connections, applicable Premium licensing and policy checks are needed.
Formatting cannot upgrade review status, broaden access, select recipients or
retry sends. Do not weaken authentication, labels or sharing to permit conversion.

## Public scope and hosting

Only the exact approved real-case derivatives and generic reference are eligible.
No installer, raw app/solution, private originals, diagnostics, unrelated mailbox
material, previous example, previous QA or previous publication history is included.
Private historical material remains outside the public allowlists.

The replacement public repository/Pages are **planned, not created or verified**
by this preparation. The parent owns a clean-history deployment and its public
HTTP verification. Target repository/URL and unverified flags live only in
`content.json`. No GitHub, model, upload, mail or runtime action is performed here.

Publish only `_public-repository`, never the working directory. The manifest
lists all repository/Pages paths and hashes; `PRIVACY-REPORT.json` binds scoped
screening to the exact public bytes without publishing private screening terms.
`.gitattributes` preserves exact bytes across Windows and Linux.

## Local preparation

Use available Python with Pillow, Playwright and pypdf for local QA only.
No runtime dependency is installed or hosted by this website.

```powershell
python .\tools\generate_content.py
python .\tools\build_home.py
python .\tools\prepare_real_example.py
python .\tools\make_manifest.py
python .\tools\serve_preview.py --base-path /preview/
```

The example helper without input arguments verifies the current fourteen
published files and rebuilds the deterministic archive/reader. First intake
accepts only the separately supplied, exact parent-approved candidate.
Private originals and review bookkeeping are not inputs.

Fresh QA verifies desktop/mobile themes, full-size keyboard image inspection,
complete TXT/HTML roundtrips, local print completeness, every download and
scoped privacy. QA captures and local PDFs remain private; public QA is a new
summary, not inherited historical results. Parent-reviewed deployment configuration
may be added separately; this preparation creates or invokes no GitHub workflow.
After final review, `tools/stage_site.py --repository` produces the exact public
repository copy; running `tools/stage_site.py` there produces `_site` with only
the declared Pages files. The parent can publish that output through its chosen
clean-history hosting configuration. `.nojekyll` prevents static-file rewriting
when branch-based Pages hosting is used.
