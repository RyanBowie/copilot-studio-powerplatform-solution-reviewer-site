# Solution Reviewer — Word output and solution download

A static Clawpilot-themed site with **directly importable 3.3.2.7 unmanaged
reviewer and automation solutions**, separate post-import setup resources,
a redacted native Word example, and the unchanged
**Data Entry Testing** real-canvas walkthrough on revision **3.3.2.5**.
The new Word example is a separate synthetic format-only test, not a Word
version of that historical 4/5 assessment. There is no upload/chat backend, telemetry, tracking,
external font or runtime service on this website.

All four public HTML pages share the benchmark's purple/neutral screen palette
through `site.css`, layered over the original Clawpilot `--cp-*` variables.
The existing `?scoutTheme=light` / `?scoutTheme=dark` override, system-preference
detection and per-page toggle remain unchanged. Hero titles use the benchmark's
blue-to-purple-to-magenta text gradient, with solid print and forced-color
fallbacks. Screenshots, report content and release packages are not restyled
or regenerated. The readers retain their existing light print palette.

**Generation is fail-closed.** The matched outcome, counts, invocation total,
citation and receipt proof come only from reviewed terminal-run provenance.
Missing inputs never fall back to the historical example, predict acceptance,
manufacture screenshots or create review sign-offs. Existing hosting status
does not mean this revision has been deployed or live-verified.

## Importable solutions and setup

| Import order | Direct Power Platform import input | Retained implementation |
| --- | --- | --- |
| 1 | [Reviewer 3.3.2.7](downloads/psr_PowerPlatformSolutionReviewer_3_3_2_7_unmanaged.zip) | Existing agent, all 19 components, 225-action collector, 21-action Word helper |
| 2 | [Automation 3.3.2.7](downloads/psr_PowerPlatformSolutionAutomation_3_3_2_7_unmanaged.zip) | Complete 500-action automatic-review implementation |

[Import and setup instructions](downloads/SOLUTION-IMPORT-SETUP.md) ·
[Setup resources ZIP](downloads/solution-reviewer-setup-3.3.2.7.zip) ·
[Exact file/member hashes and native import evidence](downloads/solution-import-release.json)

These are genuine unmanaged solution ZIPs, **not portable substitution
templates or an outer bundle**. They derive from the pinned native reviewer
and automation exports, with the complete historical automatic Word overlay
retained. Ordinary target settings are now 24 unconfigured native environment
variables; eight logical connection references ship unbound. No private
tenant bindings, credentials, connection instances or working demo defaults
are included. The source hashes are recorded in the release manifest.

1. Import the reviewer first, then automation into an explicitly authorized
   clean target. Disable workflow activation and agent publication; do not
   overwrite unrelated components. Verify the complete imported contents.
2. Keep both unchanged solution ZIPs beside `release-manifest.json` from the
   extracted setup resources. That archive is **not** a solution import input.
   Install its declared dependency with `python -m pip install -r requirements.txt`.
3. Follow the setup instructions to verify the target owner and existing
   connections, approve private storage, upload the exact unchanged Word
   template separately, and verify its real schema. Configure native values
   using the post-import helper's explicit `--apply` and
   `--confirm-environment` gates. Setup ends stopped/unpublished, readiness
   false, control Disabled and email false.
4. Publication, manual enablement and smoke checks, automatic exact-source
   acceptance, ongoing activation and any narrow email authorization are
   **separate deliberate steps**, not installation side effects. Preserve
   caller Invoker collection, explicit owner/service output and requester-only
   report-item Read; no maker fallback or broader sharing.

**Native import-only acceptance, 2026-09-21:** both exact ZIPs imported once
into one same-tenant sandbox. Fresh read-only verification passed 274 required
checks and 18 additional integrity checks: complete workflow definitions and
all 19 agent component bodies matched exactly; memberships were 38/30; all
three flows remained stopped, the agent unpublished, eight references unbound,
and 24 definitions empty with zero current-value records. No setup, template
upload, binding, activation, publication, runtime invocation or email was performed.
This is **not configured Word, automatic runtime, cross-tenant, or separate
least-privilege requester acceptance**.

An initial local comparison incorrectly decoded UTF-8 receipts as Windows-1252.
The original failed comparison is preserved privately and explicitly superseded.
Raw authenticated responses, independently parsed using strict UTF-8 in Node
and Python, confirmed full exact definition equality without text normalization,
target repair, package changes or reimport.

**Distribution approved:** parent safety review and user authorization cover
these exact release artifacts. The publication gate requires both exact native
definition/state acceptance and that separate approval. GitHub Pages deployment
and live-download verification are separate from native runtime acceptance.

## Word output and historical distribution

[Historical 3.3.2.6 configurable bundle](downloads/solution-reviewer-word-output-3.3.2.6.bundle.zip) ·
[Historical configure-before-import instructions](downloads/WORD-OUTPUT-SETUP.md) ·
[Word template](downloads/current-review-v4.3.1.web.template.docx) ·
[Redacted Word example](examples/word-output/review-example.docx) ·
[Release hashes](downloads/word-output-release.json)

The **existing reviewer**, not a separate agent, formats its finalized review
using Word Online (Business), saves a run-specific DOCX beneath the existing
`SolutionPackages\Results\solution-<safe-filename>` folder, grants the established
requester Read on that report, then returns its real URL. No separate private
Word-output storage is required. Source collection stays caller Invoker;
output connectors use explicit configured owner/service bindings. Original
TXT/JSON audit evidence and existing email policy are retained.

The native synthetic-fixture regeneration preserved the review content and
rendered as **two pages in Word for web and desktop Word**. The public example
is a privacy-redacted derivative of that actual native output. Its two preview
images are local renderings of the derivative, not fabricated native captures.
The requester was also the existing site owner; this is not separate
least-privilege-account evidence. Visual headings do not provide Word
Heading 1/outline semantics.

The historical 3.3.2.6 bundle contains real reviewer and automation solution templates, the
matching generic Word template and target-configuration tooling. **Configure
and repack before import applies only to that historical distribution**, not
the direct 3.3.2.7 ZIPs above. Neither the old outer bundle nor the unconfigured
`*.portable.template.zip` files are direct import inputs. Use your own
connections, storage, requester policy and actually discovered Word template
schema. Word Online (Business) licensing and policy approval are required.

The pinned native exports contain the reviewer's Word-enabled draft.
The automatic Word definition is an explicitly derived, local-only candidate
over the exported automatic baseline. **The demo's published agent and
automatic flow were not updated with Word output.** No native automatic Word
run, cross-tenant installation or production readiness is claimed by this
download; target import and activation need their own acceptance.

## Historical real-canvas six-stage journey

1. **Native upload menu and confirmed row.** The genuine original canvas solution
   ZIP is uploaded directly to approved private Incoming storage.
2. **Actual matching flow run.** SharePoint's **When a file is created
   (properties only)** trigger (`GetOnNewFileItems`) polls
   `SolutionPackages/Incoming` every minute, not instant delivery. Enabled-intake,
   authorization and file-scope checks gate processing. Only eligible `.zip` /
   `.msapp` files directly in Incoming qualify—not empty folders or files in
   new subfolders.
3. **Actual matching agent action.** `ExecuteCopilotAsyncV2` supplies evidence to
   the standard Copilot Studio agent without a chat prompt. The agent does not
   watch storage independently or execute the submitted app.
4. **Saved MAIN and accepted component.** The matched report and accepted screen
   assessment are shown in real native views; the complete files are linked.
5. **Verified received email.** The matching owner Inbox message and expected
   protected-report link are verified, not inferred from a send action or preview.
6. **Native full-report views.** Assessment and verification/omission views lead
   to the complete matching reader and Markdown/TXT downloads.

Nine reviewed native screenshots are used, with honest captions about capture
chronology, crops, masks and viewport limits. Their presentation order is not a
claim of a continuous recording or an unrecorded click. Configuration explainers
and the original notification-body image are not substitutes for current proof.

## Complete output and evidence boundaries

[Full matched reader](walkthrough.html) ·
[Full Markdown derivative](examples/walkthrough-325/complete-review.md) ·
[Authoritative MAIN TXT](examples/walkthrough-325/MAIN.txt) ·
[Matched provenance and public derivative hashes](examples/walkthrough-325/provenance.json)

The complete MAIN retains all ten sections, canonical records, unavailable
records, findings, strengths, verification items, omissions and full footer.
Each accepted component TXT plus the full inventory and coverage JSON is also
downloadable and fully readable in HTML **without JavaScript**.

Markdown is a **presentation-only full derivative**, not new findings, a new
assessment or a summary. Full source sections are fenced with collision-safe
delimiters. Their UTF-8 bytes can be recovered exactly, including BOM, CRLF,
literal markup, backticks and a missing final newline. TXT/JSON remains
authoritative and is never rewritten. HTML escapes report markup and changes
only browser-mandated newline representation; whole DOM/source equality is
tested. No canonical record is shortened to fit a viewport.

All five selected original files were acquired completely. **326/326 screen
lines supplied does not prove every line was semantically examined.** The
denominator is five selected-source assessments, not every file in the solution;
assessment acceptance is **not an app pass rate**. Unavailable assessments are
validation outcomes, not confirmed application defects. In earlier benchmarks,
C2/C5 remained unavailable because of evidence/response-validation failures.

Component records are AI-generated. **MAIN is deterministic assembly of
native-flow-accepted canonical records**, not another model inference, repaired
failed response or regrade. Invocation totals are logical agent invocations,
not internal model inference counts.

Current official checker, compilation, source-app/role/workflow import and
runtime/accessibility execution remain **NOT RUN**. Embedded checker records
are historical; retained syntax/default/fallback wording is not compiler or
runtime proof. No production, cross-tenant or whole-application certification
is claimed. The **bounded combined target is achieved in ONE matched run only
when its reviewed provenance establishes all of these together:** at least
4/5 accepted, valid MAIN, all five selected original sources acquired completely,
accepted C4 with complete screen input, and an accepted last-quarter screen
citation. For 326 lines, that means **line 245 or later**, not line 244.

The homepage, reader, Markdown and generated `content.json` use the same
conditional one-run statement. A 4/5 result is rendered as **4/5**, including
the full accepted C2 report when C2 is accepted; it is never relabeled 3/5.
Without every target condition, the combined target is **not established**,
even if the acceptance count is four. The statement does not establish repeated
at-least-4/5 performance or **90% reliability across different exports**.
Missing source/citation measurements, Inbox proof or public approval cannot be
replaced with predictions; the reviewed-input publication gate still applies.

## Delivery proof is bounded

The reviewed matched-run contract requires native `SendEmailV2` success,
verified owner Inbox receipt, the expected protected-report link and restored
controls. Delivery is for the exact authorized source/version and verified demo
owner, without Cc/Bcc or mail retry. The model cannot select recipients.

Existing forwarding keeps the original mailbox copy. **Forwarded corporate
receipt is not established.** Mailbox settings are not changed. No exactly-once,
all-client rendering or wider recipient-containment guarantee follows from
these observations. The original historical run's unverified-Inbox caveat
belongs to that historical evidence, not the primary improved walkthrough.

## History remains intact and separate

[Historical complete reader](full-example.html) ·
[Historical exact 14-file archive](downloads/real-canvas-review-example.zip) ·
[Historical input/published hashes](downloads/real-canvas-example-manifest.json)

The historical **1/5** example retains its four original approved TXT files,
eight image derivatives and two published provenance records without rewriting
their bytes. C4 had an **80/326-line** prefix and six model calls. The complete
**58,939-byte coverage** appendix and original notification/capture limitations
remain available. The historical archive's exact bytes and member hashes remain
pinned; it contains reports/images/provenance, not an installable app.

The **two no-email benchmark runs** on unchanged 3.3.2.5 are separate again:
each accepted **3/5**, had valid MAIN, supplied 326 screen lines, and cited through
line 285. They used 7 and 9 logical agent invocations. Neither supplies the new
walkthrough's email or screenshots. The combined 4/5 target remained unmet in
those two benchmarks; two runs of one export do not demonstrate 90% reliability
across different exports.

[Separate benchmark reader](follow-up.html) ·
[Complete benchmark MAIN](examples/follow-up/complete-review.txt) ·
[All 11 historical comparisons, including regressions](examples/follow-up/results.json) ·
[Benchmark provenance](examples/follow-up/provenance.json)

Earlier 4/5 results with invalid MAIN and 0/5 regressions remain visible. Larger
files/chunking, reliable original-path mapping and broader supported-export
evaluation remain work to do. Failed and unsupported sources stay visible.

## Generic architecture, reference and formatting

The current **GPT5Chat** configuration uses the standard Copilot Studio harness,
not the GitHub Copilot harness. **GPT-5 Reasoning is not required.** Choose a
supported model available in your environment and evaluate grounded output,
structured-response reliability, latency and cost. Historic headers retain the
model actually used at the time; model choice does not confer readiness.
The canonical 3.3.2.7 packages and setup specifically pin **GPT5Chat**. A model
change is a new revision requiring fresh verification, not permission to bypass
the target availability or canonical-definition checks.

Manual: consent topic → `CollectReviewEvidence` via `InvokeFlowTaskAction` →
caller-owned OneDrive **Invoker** → source advice. Automation uses SharePoint
events, bounded native extraction, the published agent, protected reports and
separately guarded mail. Flow capabilities are not arbitrary model-controlled
tools. Trusted internal exports are the limited scope, not hardened
hostile-archive processing. No hosted Python/Azure worker is required.

The setup, tool/topic reference and workflow architecture remain available on
the homepage. The new distribution adds the deterministic presentation topic
and existing reviewer's Word tool. All target connections and flow/template
bindings require explicit configuration; the demo's private locations and
connection instances are not shipped as working defaults.

Browser **Print / Save as PDF** is a presentation option, tested for full content.
Native DOCX output is implemented in the existing reviewer draft/helper.
Automated PDF generation is **not implemented**. Word Online (Business)
formatting uses a controlled supported template, the existing Results folder,
explicit owner/service connections, licensing and policy checks.
Formatting cannot upgrade status, broaden access, change recipients or retry
mail. Never weaken authentication, labels or sharing for conversion.

## Required reviewed input contract

The parent supplies `examples\walkthrough-325\provenance.json` and only its
reviewed derivative files after the real run and private review. Schema version
1 is strict: unknown keys, duplicate keys, path traversal, unlisted files,
missing proof, wrong roles, altered bytes and PNG metadata fail validation.
There are no private IDs, tenant URLs, mailbox addresses or raw-source
fingerprints in public provenance.

Required top-level fields:

- `schemaVersion`: integer 1.
- `kind`: `REVIEWED_GENUINE_CANVAS_EMAIL_WALKTHROUGH`.
- `approvedPublicDerivatives`, `mainValid`, `allFiveSelectedSourcesComplete`:
  literal `true` **only after actual parent review/verification**.
- `sourceDisplayName`: `Data Entry Testing`; `revision`: `3.3.2.5`;
  `outcome`: actual terminal `ReviewPartial`.
- `accepted`, `selected`, `unavailable`: actual integer counts,
  `accepted >= 3`, `accepted + unavailable == selected == 5`.
- `acceptedPassIds`: unique actual C1–C5 IDs, count matching `accepted`;
  C4 must be accepted for this screen walkthrough.
- `logicalAgentInvocations`: actual integer within the existing 13-call ceiling.
- `screenLinesSupplied`, `totalScreenLines`: 326; `latestScreenCitation`: actual
  integer between 1 and 326, not an anticipated citation.
- `email`: `nativeSendStatus` is `Succeeded`;
  `ownerInboxReceiptVerified`, `expectedReportLinkVerified`, `controlsRestored`
  are literal verified `true`; `forwardedCorporateReceiptVerified` is `false`.
- `images`: exactly the nine rows below, each with `file`, `role`, positive
  `bytes`, lowercase SHA-256, safe plain-text `alt` and `caption`.
- `reports`: each with `file`, `role`, positive `bytes` and lowercase SHA-256.

| Image role | Required filename |
| --- | --- |
| uploadMenu | native-upload-menu.png |
| uploadedRow | native-upload-confirmed.png |
| flowRun | native-flow-run.png |
| agentHandoff | native-agent-handoff.png |
| mainOpening | native-main-opening.png |
| component | native-component.png |
| email | native-email-received.png |
| mainAssessments | native-main-assessments.png |
| mainVerification | native-main-verification.png |

Reports: `MAIN.txt` (`main`), one `C1.txt`–`C5.txt` per actual accepted pass
(`component`), `inventory.json` (`inventory`), `coverage.json` (`coverage`).
For a reviewed 4/5 result with C1/C2/C3/C4 accepted, all four complete TXT files,
including **C2.txt**, are required; a different actual accepted set must supply
its corresponding complete approved TXT files. Never substitute
reports from a benchmark run. `complete-review.md` is generated locally, not a
parent input. A missing native screenshot is a blocker, not a placeholder slot.

Private visual reviews remain under `_private-hold`, never the public input
directory. `check_public.py` requires **three separate hash-bound review files**:

- `--image-review`: all eight historical image pins.
- `--walkthrough-image-review`: all nine new image pins.
- `--word-image-review`: both locally rendered redacted Word page pins.

Each has `visualReviewComplete` set to literal `true` by the actual reviewer,
and `images` containing exactly one `file`, `sha256`, `text` record per image.
`file` can be a basename or exact corresponding relative public path; `text`
is reviewed offline OCR, including an explicit empty string when appropriate.
The tool never supplies sign-offs itself. All sets are decoded, checked for
metadata and screened against the same supplied private patterns. OCR and
restricted patterns are never published.

## Local build and review — no publication

Run from this `public-site` directory, using existing Python with Pillow,
Playwright and pypdf. Tests create explicitly synthetic **private** fixtures
under `_private-hold` and remove them. Unit fixtures never become public
evidence; the separately reviewed public synthetic Word example has its own
native provenance and explicit scope.

```powershell
python -m unittest discover -s tools -p 'test_*.py'
python tools\generate_content.py
python tools\build_home.py
python tools\build_walkthrough.py
python tools\prepare_real_example.py
python tools\build_followup.py
python tools\make_manifest.py
python tools\serve_preview.py --base-path /preview/
```

The first manifest intentionally remains `LOCAL_REVIEW_PENDING` until current
QA and privacy pins match. In another local terminal, choose a **new** capture
directory and the parent's actual private review/pattern files:

```powershell
python tools\qa_site.py --base-url http://127.0.0.1:4178/preview/ --capture-directory _private-hold\walkthrough-qa-01
python tools\check_public.py --private-patterns _private-hold\private-patterns.json --image-review _private-hold\historical-image-review.json --walkthrough-image-review _private-hold\walkthrough-image-review.json --word-image-review _private-hold\word-image-review.json
python tools\make_manifest.py
python tools\build_walkthrough.py --verify-only
```

QA covers primary matching images/counts/receipt, all historical and benchmark
readers, complete DOM/text equality, lossless Markdown, real downloads, keyboard
image inspection, mobile/light/dark layouts, no-JavaScript content, all anchors,
actual browser PDF completeness and blocked nonpublic paths/external requests.
All QA captures and PDFs remain private; a fresh summary binds all relevant
current files, not just `content.json`.

Only explicit public paths in `tools\public_inventory.py` may be screened or
staged. The new component-report path set is selected from validated provenance,
never directory globbing. The historical 14-file ZIP remains exact. The new
Word bundle, both DOCX downloads, direct solution ZIPs and supplementary setup
archive are recursively inspected, with exact
asset/member hashes and an explicit reviewed structural-identifier inventory.
Necessary component/document IDs are allowed only within the reviewed release
contexts, never globally; private restriction patterns remain enforced.
`.gitattributes` preserves bytes across operating systems.

After parent final review, `tools\stage_site.py --repository` can produce an
exact repository copy, and `tools\stage_site.py` an exact `_site` tree. Both
refuse existing targets and missing/stale approval, inputs or pins. They do not
push or publish. The checked-in Pages workflow only stages that exact reviewed
tree; missing matched-run evidence cannot be deployed through it. The parent
alone owns publication, native runtime, email, screenshots and final review.
For a new isolated repository stage, use
`python tools\stage_site.py --repository --output _private-hold\word-release-stage`.
The new Word manifest is mandatory for publication; old installer-exclusion
flags cannot substitute for the actual reviewed solution files.
The import-first manifest additionally pins both real ZIPs and sanitized
artifact-specific native receipts. Successful import jobs or matching action
counts alone do not satisfy its exact-definition gate. Parent permission to
distribute new downloads remains separate from the reviewed historical evidence.
