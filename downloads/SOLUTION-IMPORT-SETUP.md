# PSR 3.3.2.7 — import first, configure afterward

This support directory configures the **existing, complete native reviewer** after
both release solutions are imported. It does not generate/repack ZIPs, stamp
installation IDs into solution descriptions, import solutions, create connections,
upload templates, publish an agent, invoke/replay a flow, or send a message/email.
Importing a solution or setting a native environment variable is **not**
authorization to run it.

**Evidence boundary:** the bundled regressions are offline mocks, not proof of
target import, native compilation, connector behavior, or execution of the
500-action automatic candidate. Do not represent this release as natively accepted
until the target owner has observed and accepted its real exact-source run.

## 1. Import the canonical solutions unchanged

Use an explicitly authorized, clean **target**, never the protected source.
Import the reviewer solution first, then its automatic-review solution, using the
release's canonical ZIPs. Both solution versions must be `3.3.2.7`; their static
description must be exactly:

```text
PSR import-first release 3.3.2.7
```

Do not enable workflows, publish the agent, force overwrite unrelated components,
or populate target environment-variable current values during import. Do not
modify the canonical packages. Existing connections may be selected only if they
are the explicit target owner's correct connector instances. No maker-connection
fallback is allowed. If the importer cannot accept the unconfigured native
definitions, **stop and retain the native import error**; these scripts do not
hide an importability failure by removing actions, changing the renderer, or
manufacturing runtime acceptance.

Expected imported state:

| Component | Complete action count | Required state |
|---|---:|---|
| Native evidence collector | 225 | Stopped; source reads Invoker |
| Native Word helper | 21 | Stopped; output connections Embedded |
| Automatic review | 500 | Stopped; Embedded; `psrDeploymentReady=false` |
| Existing reviewer agent, all 19 components | — | Unpublished; no publish-on-import |

Workflow discovery uses the structural IDs in the native release. The target bot
and its components are discovered by their exact schema names, not a source bot or
environment ID. Full solution membership, owner, connection references, native
definitions, GPT5Chat model, authentication, component data, and the sealed
rawSource/admission kernel must match. An extra component, foreign owner, custom
solution membership, active run, previous publication, or definition drift stops
setup. Source environment identity is guarded by a fixed SHA-256.

## 2. Prepare target configuration and resources

Prerequisites: Python 3.10+, the declared PyYAML dependency, Azure CLI already
authenticated by the operator to the target owner, six **existing** owner
connections, an existing provisioned owner OneDrive, and an approved owner-private
SharePoint site. This client retrieves delegated tokens only when an operator runs
a target command; it never performs login or connection creation.

The six connectors are SharePoint, OneDrive for Business, Office 365 Users,
Microsoft Copilot Studio, Office 365 Outlook, and Word Online (Business). There are
eight logical references; Directory and SharePoint are shared native dependencies.
Verify licensing, target GPT5Chat availability, DLP, premium Word entitlement,
and the agent's authenticated audience. `availabilityVerifiedInTarget` and
`authenticationReviewedInTarget` are explicit operator attestations, **not**
automated licensing/audience certification.

Copy `target.example.json` to private `target.json`. Fill every empty target field
with a verified real value. Use lowercase complete GUIDs and a new installation GUID. Keep
`manualInboxName` fixed at `PowerPlatformSolutionReviewInbox` and the model fixed
at `GPT5Chat`. Choose unused safe list/library names. Empty URLs, identities, and
connection IDs deliberately fail validation; no fake destination is supplied.

The site must have direct Full Control only for the owner; explicit extra site
administrators or broad root Read/Edit grants are rejected. Only the exact sole
Limited Access traversal role from item sharing is ignored. Lists must inherit
this private site, enable versioning, and carry this installation's exact marker.
The job key is unique/indexed. Existing unrelated resources are never renamed,
overwritten, repermissioned, or adopted just because solutions have been imported.
There is no requirement that resources be created before import.

### Verify the exact Word template before binding

The operator separately uploads the bundled generic
`current-review-v4.3.1.web.template.docx`, without opening or editing it, as a
physical file in the verified owner's default OneDrive root. Do not overwrite an
unrelated file. A different safe filename is permitted if configured explicitly,
but the bytes must remain:

```text
498ee9eb6d1fbd9df4fa719a873fa57237fdbf224fcb6c62c77c96881bac3065
```

The helper proves default-drive ownership using Graph and the owner connection,
reads the file through that connection, verifies its hash, obtains the target Word
schema, and rechecks the file ETag. Shortcuts, other people's drives, or an
unprovisioned drive are not accepted.

The schema must be the exact root array/object structure with:

* `940007`: string `ReviewIdentity`
* `940008`: array `ReviewBlocks`, object items containing exactly string
  `BlockHeading`, `LeadText`, `BodyText`, `NestedText`, and `CodeText`
* `940009`: string `NativeRunStamp`
* `940010`: string `PresentationNotes`

Only descriptive `title`/`description` metadata may vary; all structural keywords,
summaries, numeric keys, types, and children are checked. A changed schema is a
**STOP**, not a reason to remove or rewrite the renderer. Word source remains
constant `me`; numeric property keys are not environment variables.
`psr_WORD_DRIVE` and `psr_WORD_FILE` are written only after this proof succeeds.

## 3. Verify and set up the imported release

Place `release-manifest.json` beside its canonical ZIPs. The support scripts,
`kernel-selector.json`, `sharepoint-schema.json`, and exact DOCX stay together.
When the manifest is in another directory, pass `--manifest` on every command:

```powershell
python .\install.py plan --manifest .\release-manifest.json --config .\target.json
python .\install.py verify-import --manifest .\release-manifest.json --config .\target.json
python .\install.py setup --manifest .\release-manifest.json --config .\target.json --state .\psr-target-state.json --apply --confirm-environment "<exact-target-environment-guid>"
python .\install.py verify --manifest .\release-manifest.json --config .\target.json --state .\psr-target-state.json
```

`plan` is entirely offline and writes nothing. `verify-import` and `verify` read the
target but write neither target nor ledger. **Every mutating operation**, including
local acceptance/authorization records, requires both `--apply` and the exact
`--confirm-environment` value. No command defaults to activation.

Setup order is enforced:

1. Validate configuration, target/tenant/user identity, connections, native release
   and full membership/ownership; prove the Word file/schema and check collisions.
2. Recheck the canonical target, then establish a post-import claim using the
   native **`psr_INSTALLATION_ID` current value plus the local ledger**.
3. Create only installation-marked owner-private resources and the actual target
   agent's disabled/no-email control record. Verify the physical private caller
   Inbox; no notification or broad access is granted.
4. Bind only the verified owner connections; write ordinary native current values.
   Native definition schemas and flow parameters are identically named
   `psr_<TOKEN>` and have empty String defaults. The workflow definitions are
   not rewritten to inject target literals.
5. Recheck everything. Finish with **all three flows stopped**, readiness false,
   agent unpublished, control `Disabled`, email false, and **no acceptance,
   publication prerequisite, source authorization, or email authorization**.

The marker is claimed only after canonical validation. Its first-value creation
uses a transactional compare-and-swap on the definition ETag and current value.
The claim intent is saved locally first so a crash does not justify silent
adoption. A native marker with no matching ledger, a different marker/value ID,
multiple current values, or a stale ETag stops. Preserve the private ledger.
No wildcard ETag or silent 412 retry is used.

## 4. Separate publication, manual smoke, and automatic acceptance

These are explicit subsequent operations, never part of installation.

1. Review the actual target agent in Copilot Studio: Integrated authentication,
   Always authentication trigger, GroupMembership access, approved audience,
   constant GPT5Chat, and every existing topic/tool. Publish it **separately** only
   with authorization. The helper has no publishing API.
2. With all flows still stopped/readiness false and control Disabled, run
   `publication-prerequisite` with the two mutation flags. It verifies successful
   synchronized publication and the owner connector's actual agent picker, then
   writes the native publication metadata. It does not publish or enable anything.
   This configuration change invalidates earlier acceptance.
3. Run `enable-manual` with the mutation flags. Only collector and Word helper
   are enabled; automatic flow/readiness/control/email remain off.
4. Perform an explicitly authorized manual smoke with a tiny harmless synthetic
   trusted original-extension ZIP/MSAPP in the caller's **own** physical private
   `PowerPlatformSolutionReviewInbox`. The helper never uploads or invokes it.
   Verify real review/Word content, audit/coverage boundaries, native stamp,
   browser/desktop readability, requester **Read on the report item only**, and
   **no sharing notification/email**. Do not change site/library root access.
5. Create a private evidence JSON only after observing those properties:

   ```json
   {
     "syntheticOnly": true,
     "wordContentReviewed": true,
     "requesterReadOnlyVerified": true,
     "noSharingNotificationVerified": true,
     "noEmail": true
   }
   ```

   Run `record-manual-smoke` with `--collector-run`, `--word-run`, `--evidence`,
   `--confirm-harmless-test`, and the mutation flags. Both actual native runs must
   have succeeded after the current configuration. This is not automatic-path
   acceptance or a claim that a distinct least-privilege recipient was tested.
6. Run `arm-test --confirm-harmless-test` with the mutation flags. This is the
   **first explicit automatic activation boundary**: it sets only the separate
   readiness Boolean, starts the automatic flow, and sets `SyntheticValidation`
   with no approved source and email false. Canonical actions/kernel remain exact.
7. Upload one authorized tiny synthetic new source to Incoming, obtain its actual
   metadata with `inspect-incoming`, then run `approve-source --source-id "<UniqueId>"
   --version "<UIVersionLabel>" --confirm-harmless-test` with the mutation flags.
   Only that exact current file/version is approved. The native created-only gate
   can occur before approval; a missed window is **not** success or permission to
   replay an old event. Pause, review, and authorize a fresh test.
8. Observe the real completed native automatic run and Word output. Record its
   exact job using `accept-test --job-id "<actual-guid>" --evidence .\evidence.json`
   plus the mutation flags. The native run must succeed; the job must match the
   authorized source/version with `NotAttempted` email; MAIN/coverage and detailed
   source accounting must pass. Visual and item-security assertions are operator
   observations, not something this CLI fabricates.
9. `activate` with the mutation flags is separate approval for ongoing automatic
   operation of that exact accepted revision. It leaves email **false**. Any
   changed configuration, native current value, owner, template ETag/schema,
   canonical definition, reference, or publication invalidates the pinned proof.

For a separately authorized email test, remain in `SyntheticValidation` after
acceptance and use `authorize-email-source` with exact source/version,
`--confirm-harmless-test`, `--confirm-email-recipient "<exact-owner-mail>"`, and both
mutation flags. It cannot authorize general Enabled-mode email. Existing
verified-recipient and at-most-one-attempt runtime rules remain unchanged. The
helper itself never sends or replays. Revoke using `pause`.

`pause` explicitly disables control/email, stops all three flows, resets the
readiness latch, and clears acceptance/source/email authorization. It does not
unpublish the agent. Stop/unpublish separately before rerunning full setup.
No helper silently disables an unexpectedly active fresh import to make its
verification pass.

## Concurrency, drift, and troubleshooting

* **Version/definition/membership/owner drift:** stop. Preserve evidence; do not
  delete the marker/ledger or label a foreign solution as this installation.
* **Unexpected active/published import:** setup will not claim it. Investigate and
  use a clean authorized target or perform a separately approved reset.
* **Word hash/schema mismatch:** upload the byte-exact file separately or correct
  the supported target schema. Do not edit numeric keys, substitute a template,
  remove Word actions, or treat a failure as successful import/runtime.
* **Connection owner/account mismatch:** fix the explicitly chosen owner
  connection separately. Shared access is not ownership. A nonempty foreign
  reference is never rebound automatically, including a previously configured
  instance after a configuration change.
* **Existing unmarked resources/Inbox:** choose unused resource names or perform
  deliberate administrative cleanup outside this helper. The caller Inbox name
  is fixed. A partial Inbox creation without its final marker must be inspected
  by the owner, not adopted using an ACL-only fallback.
* **Pagination/missing ETags/API schema uncertainty:** stop rather than accept
  incomplete ownership/privacy proof. This release intentionally has no broad
  list scan, wildcard concurrency fallback, or privileged maker impersonation.
* **412, pending ledger, or pending readiness mutation:** inspect authoritative
  state and the saved intent. No automatic ETag retry/roll-forward occurs.
  A failed first setup may be rerun only with the matching ledger/marker and
  still-stopped unpublished canonical release. If readiness changed before a
  crash, the operator must reconcile that deliberate transition; deleting the
  ledger is not recovery.
* **Drift while active:** authorization fails closed, but the CLI cannot
  retroactively revoke already running external work from an untrusted snapshot.
  Use separately authorized platform controls to stop runs/flows and disable
  control/email immediately, then investigate. Do not claim this tool is a
  continuous monitor or an emergency bypass around ownership validation.
* **Changing configuration:** stop the installation and unpublish as appropriate,
  then rerun setup with mutation confirmation. Acceptance is invalidated before
  target setup writes, including on failure. Read-only checks report invalid
  proofs but do not mutate the ledger. No old acceptance can authorize activation
  against changed native values.

## Offline validation and packaging contract

This public-support ZIP intentionally excludes synthetic regression fixtures and
the author-only privacy scanner. Both remain unchanged in private authoring
source with the full validation reports. Runtime ownership, target identity,
configuration and activation guards have not been removed or weakened.

Private tests block real network/auth entry points and do not claim native
service acceptance. Packaging must additionally call `Release` against the
**final** release manifest/ZIPs, with no API client, after canonical ZIP generation.
Run `python .\verify_release.py .\release-manifest.json` for that offline check.
Required manifest fields and the CLI/package boundary are described by
`release-manifest.schema.json`. The loader obtains native component inventory,
schema names, bot data/configuration, connection references, and environment
definitions directly from the hashed canonical ZIPs; an inventory in the manifest
is supplementary provenance, not permission to skip native components.

Until the final ZIPs and manifest have passed that offline loader check plus the
packager's PAC/native-schema validation, do not advertise the support bundle as
integrated with a finalized release. Offline validation alone still says nothing
about upstream native 500-action import/runtime acceptance.
