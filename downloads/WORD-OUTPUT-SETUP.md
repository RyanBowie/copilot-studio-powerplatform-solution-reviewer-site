# Word-enabled portable release 3.3.2.6

**DERIVED, configure before import.** This is the existing Power Platform Solution
Reviewer, its native evidence collector and Word helper, plus the automatic-review
Word candidate. It is not a separate Word-test agent, an already configured tenant
export, or an automatic deployment.

The reviewer package starts from an authentic fresh export containing all 19
current draft components, including the accepted v4.3.1 Word formatter/action/topic
and native helper. The automation package starts from the authentic deployed
3.3.2.5 baseline and explicitly overlays the sealed, locally validated 3.3.2.6 Word
candidate. Both solution manifests are versioned 3.3.2.6. Historical releases and
the source tenant's published agent/automatic release are unchanged.

## What is proven

The source reviewer draft/helper created a real native Word report from an already
completed **synthetic fixture** review: two readable pages in Word web and desktop,
95 semantic fields, 52 populated paragraphs, four parent groups and 11 child
indents, exact retained audit content, native run stamp and requester report Read.
That was format-only regeneration, not another package assessment. The requester
was the existing site owner; a separate least-privilege recipient was not tested.

This distribution has official **local PAC pack/unpack**, complete dependency and
target-token checks, focused offline installer/Word regressions and two synthetic
target configurations. **No cross-tenant import, target native compilation/runtime
or automatic native Word execution is claimed.** See `VALIDATION.json`.

Dynamic headings use visible character formatting, not built-in Heading 1/outline
navigation. Continuation lines use native hanging indentation. The template uses
one populated paragraph per repeat: no hidden empty paragraphs, post-generation
OOXML cleanup service, HTML-to-Word shortcut or guaranteed page count for other
reports.

## Contents and prerequisites

The bundle contains two real `*.portable.template.zip` solution packages, the exact
generic `current-review-v4.3.1.web.template.docx`, typed target configuration,
installation helpers, dependency/token inventory, setup notes and hashes.
**Never import a template ZIP directly.** First generate its target ZIP and settings.
Offline test fixtures are retained in private author validation evidence, not the
public download. The full focused regression suite and synthetic PAC preparation
checks are still run; their results are included in `VALIDATION.json`.

Use a short local Windows folder, Python 3.10+, official Power Platform CLI (`pac`)
and Azure CLI (`az`). Install the declared Python dependency with
`python -m pip install -r .\requirements.txt`. Use an explicitly authorized target
tenant/environment; the helper rejects the protected source environment.

The target requires Dataverse, Copilot Studio and an available supported model
(the current draft uses **GPT5Chat**, not a requirement for a Reasoning model).
Word Online (Business) is a **premium** connector: confirm the applicable Power
Automate/Copilot Studio licensing, target DLP and connector availability. All six
connectors must be allowed together for the intended use:
SharePoint, OneDrive for Business, Office 365 Users, Microsoft Copilot Studio,
Office 365 Outlook and Word Online (Business).

Run as the declared licensed target owner/service user with permission to import
and own the solutions/flows, use the connections, manage the approved SharePoint
resources and grant Read on generated report items. The helper verifies that all
six explicit connection instances belong to this owner and environment.
Source collection **remains Invoker**; Word/SharePoint/directory output connections
are explicitly **Embedded**. There is no maker-connection fallback for source reads.

Use the existing approved owner-private SharePoint site required by the intake and
audit contract. The helper does not privatize an unrelated site or broaden root
access. It accepts only the exact sole Limited Access traversal role introduced
by item sharing; Read/Edit/mixed/unknown root grants still fail. The owner's
OneDrive must already be provisioned. Administrative access to someone else's
drive and shared shortcuts are not ownership proof.

## 1. Configure the target and upload the generic template

Copy `target.example.json` to a private `target.json`. Fill the actual target
tenant/environment GUIDs, Dataverse/site/personal-site URLs, owner UPN and all six
connection **instance IDs**. Confirm the selected model's actual availability.
Choose unused safe list/library/Inbox names and a new installation GUID.
Replace every nonworking `__TARGET_*__` token with its actual verified target value.
Unresolved tokens are rejected, including tokens that otherwise resemble valid
connection IDs. No plausible tenant URL or mailbox is supplied as an example.

`agentAccessGroupId` is optional: leave it blank to request no additional group
assignment through import settings, or supply an existing target-approved Entra
group GUID. The helper creates no group and does not certify its membership.
The owner must review the actual authenticated agent audience before publication;
blank does not mean anonymous or organization-wide access.

Upload the bundled generic DOCX **without opening/editing it** to the declared
owner's default OneDrive root. Use OneDrive's ordinary **Upload > Files** operation.
Do not overwrite an unrelated same-name file. If needed, copy/rename the local
file without editing its bytes, upload under an unused name and set
`wordTemplateName` to that exact filename before preflight.

Required template SHA-256:
`498ee9eb6d1fbd9df4fa719a873fa57237fdbf224fcb6c62c77c96881bac3065`.
Opening it in Word web can rewrite the package and invalidate this byte check.
The helper does not upload, repair or overwrite templates.

Authenticate Azure CLI to the target tenant, then run from this extracted folder:

```powershell
python .\install.py preflight --config .\target.json
python .\install.py setup-storage --config .\target.json --apply --confirm-environment "<target-environment-guid>"
python .\install.py verify-word-template --config .\target.json
```

`setup-storage` creates/reuses only this installation's marked versioned library,
jobs/control lists, Incoming/Results/Working folders and verified private owner
Inbox. It deliberately creates **no placeholder agent/control row** before import.
Unrelated same-name resources, active controls and changed ownership are stops.

`verify-word-template` resolves the physical target file by name through the
authenticated owner's default drive, reads its bytes through the target OneDrive
connection and checks the exact hash. It then invokes the target Word connector's
**GetFileSchema** for that actual file. It discovers the four root keys by title
and verifies the five literal repeat children. No demo drive/file IDs or numeric
root IDs are assumed. State stores the actual file, ETag, schema hash and bindings.

The model is `PSR_PRESENTATION_READER_V4_3`; the formatter route is
`PSR_PRESENTATION_ONLY_V4_3`. Roots are ReviewIdentity, ReviewBlocks,
NativeRunStamp and PresentationNotes. Repeat children are BlockHeading, LeadText,
BodyText, NestedText and CodeText.

## 2. Prepare/import the reviewer, then complete setup

```powershell
python .\install.py prepare-reviewer --config .\target.json --work .\reviewer-build
```

Run the exact PAC import command returned by the helper, using its generated
`*.target.zip` and `reviewer.settings.json`. Do not add `--activate-plugins`,
`--publish-changes`, `--force-overwrite` or skip dependency checks. Both native
flows are packaged stopped and `publishOnImport` is false. Confirm that state in
the target before continuing.

```powershell
python .\install.py configure-agent --config .\target.json --apply --confirm-environment "<target-environment-guid>"
python .\install.py setup --config .\target.json --apply --confirm-environment "<target-environment-guid>"
python .\install.py enable-manual --config .\target.json --apply --confirm-environment "<target-environment-guid>"
```

These commands discover actual imported component/solution membership, verify
model/orchestration and Integrated/Always/GroupMembership authentication, create
the disabled/no-email control row with the **actual target agent ID**, and verify
both native definitions and owner-bound references before explicit activation.
The collector starts Invoker; the 21-action Word helper starts with Embedded
output connections. No review, email, publication or agent sharing is performed.

In Copilot Studio, review the target draft, audience and model/evaluation
advisories. Perform an explicitly authorized small trusted-package manual test
and inspect its real Word output/link. Other callers use their own Invoker
connection and physical private folder with the configured Inbox name, not the
owner's URL. Publish the actual target agent only after the owner's required
evaluation/acceptance, and wait for successful synchronized publication.

## 3. Prepare/import automatic Word review, still disabled

```powershell
python .\install.py prepare-automation --config .\target.json --work .\automation-build
```

This resolves the actual imported/published agent and authenticated connector
picker, publication time, owner identities, resources, control row and current
target Word schema. It binds all required values and preserves the admission
fingerprint. Shared SharePoint/directory references are reused only when proven
members of this exact marked reviewer installation with the correct owner
connection. Unrelated same-name references are not adopted.

Run the returned import command with its target ZIP/settings, without automatic
activation/publication. Then run `python .\install.py verify --config .\target.json`.
The 500-action automatic candidate remains stopped with `psrDeploymentReady=false`.

## 4. Owner-scoped target acceptance and activation

The automatic Word path has **not** been natively tested in the source release.
The owner must authorize and observe a real target created-file test before
acceptance. Email stays off:

```powershell
python .\install.py arm-test --config .\target.json --apply --confirm-environment "<target-environment-guid>"
python .\install.py inspect-incoming --config .\target.json
python .\install.py approve-source --config .\target.json --source-id "<actual-file-UniqueId>" --version "<actual-UIVersionLabel>" --apply --confirm-environment "<target-environment-guid>"
```

After arming, upload one new harmless synthetic original-extension ZIP/MSAPP to
Incoming, inspect metadata and approve that exact version before its event
authorization gate. Observe the native created-file run; if approval was missed,
pause and authorize a fresh test, not an old-event replay. The helper does not
upload, invoke, replay or send. Require the completed MAIN/detailed evidence,
coverage/NOT RUN boundaries, retained audit and correct Word content, native run
stamp, browser/desktop readability, report-only Read and usable requester link.

```powershell
python .\install.py accept-test --config .\target.json --job-id "<actual-completed-target-job-guid>"
python .\install.py activate --config .\target.json --apply --confirm-environment "<target-environment-guid>"
python .\install.py pause --config .\target.json --apply --confirm-environment "<target-environment-guid>"
```

`accept-test` checks exact-source completed job/coverage and pins the definition
and target publication; it does not inspect Word visually or certify a separate
least-privilege account. The owner performs those checks before activation.
`activate` enables only the accepted revision, with email still false. Optional
`approve-email-source` is a separate explicit exact-source owner authorization;
existing verified-recipient/at-most-one-attempt mail behavior is unchanged.

## Output and operational boundaries

Word output goes to configured **Results / solution-&lt;safe filename&gt;**, not a
separate caller-private Word destination. Each DOCX has a new native-run-specific
filename. Existing reports/audits are not overwritten. Read is granted on the
report item only, with no grant notification, and the saved requester URL is
returned after successful grant. Source/audit privacy remains unchanged.

Static strict ParseJson validation uses supported **Secure Inputs only**.
Runtime base64 equality checks model `rawSource` against the actual report before
output writes; formatting cannot silently substitute or reassess content.
The existing source/admission/confirmation and no-retry boundaries remain intact.

Keep `target.json`, installation state, generated target ZIP/settings and API
evidence private. Resume using the same configuration/state; do not mix targets.
Every mutating helper command requires `--apply` and the exact environment GUID.
On mismatch, stop and inspect rather than weakening guards or reusing another
installation's resources. Native publication/import/runtime acceptance remains
the target owner's responsibility.
