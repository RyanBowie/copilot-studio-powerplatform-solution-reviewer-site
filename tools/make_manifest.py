"""Pin a fresh approved real-example public tree; never inherit earlier case data."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from public_inventory import ALL, DEPLOY, REPOSITORY_ONLY, MANIFEST, LOCAL_DIRECTORIES
from prepare_real_example import validate_files, MANIFEST as EXAMPLE_MANIFEST
from build_followup import verify as verify_followup
from build_walkthrough import verify as verify_walkthrough, verify_outputs, primary_content, PROVENANCE as WALKTHROUGH_PROVENANCE
from build_home import build as build_home
from word_release import verify as verify_word_release, summary as word_summary, MANIFEST as WORD_MANIFEST, QA_SCOPE, PRIVACY_SCOPE, PUBLICATION_SCOPE

SITE = Path(__file__).resolve().parents[1]
c = json.loads((SITE / "content.json").read_text(encoding="utf-8"))
walkthrough = verify_walkthrough()
word = verify_word_release(required=True)
verify_outputs(walkthrough)
if c["example"] != primary_content(walkthrough):
    raise ValueError("Primary content differs from reviewed matched-run evidence.")
if (SITE / "index.html").read_bytes() != build_home(walkthrough).encode("utf-8"):
    raise ValueError("Primary homepage is stale; rebuild from matched-run evidence.")
if (not c["publication"]["approvedPublicPreview"] or not c["example"]["approvedPublicDerivatives"]
        or not c["downloads"]["installerIncluded"] or c.get("wordOutput") != word_summary(word)):
    raise ValueError("Reviewed Word release and historical derivative pins must match current files.")
script = "window.PSR_CONTENT = " + json.dumps(c, indent=2, ensure_ascii=False) + ";\n"
if (SITE / "content.js").read_text(encoding="utf-8") != script:
    raise ValueError("Regenerate current browser data.")
e = json.loads((SITE / EXAMPLE_MANIFEST).read_text(encoding="utf-8"))
validate_files(e)
followup = verify_followup()
archive_data = (SITE / e["bundle"]["path"]).read_bytes()
if hashlib.sha256(archive_data).hexdigest() != e["bundle"]["sha256"]:
    raise ValueError("Real-example archive pin mismatch.")
with ZipFile(SITE / e["bundle"]["path"]) as z:
    if len(z.namelist()) != 14 or set(z.namelist()) != {row["archivePath"] for row in e["files"]}:
        raise ValueError("Unexpected archive member closure.")
    if any(z.read(row["archivePath"]) != (SITE / row["path"]).read_bytes() for row in e["files"]):
        raise ValueError("Archive differs from the approved published files.")
found = {p.relative_to(SITE).as_posix() for p in SITE.rglob("*")
         if p.is_file() and not any(part in LOCAL_DIRECTORIES for part in p.relative_to(SITE).parts)}
if found - set(ALL):
    raise ValueError("Unexpected active file(s); only the explicit current allowlist is eligible.")
files = []
for name in ALL:
    if name == MANIFEST:
        continue
    path = SITE / name
    if not path.is_file():
        raise ValueError("Missing explicit current file: " + name)
    files.append({"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "bytes": path.stat().st_size, "deployToPages": name in DEPLOY})
qa = json.loads((SITE / "qa/RESULTS.json").read_text(encoding="utf-8"))
privacy = json.loads((SITE / "PRIVACY-REPORT.json").read_text(encoding="utf-8"))
privacy_pins = {row["path"]: row["sha256"] for row in files if row["path"] != "PRIVACY-REPORT.json"}
walkthrough_pin = hashlib.sha256((SITE / WALKTHROUGH_PROVENANCE).read_bytes()).hexdigest()
qa_pins = {name: hashlib.sha256((SITE / name).read_bytes()).hexdigest()
           for name in ALL if name not in {"qa/RESULTS.json", "PRIVACY-REPORT.json", MANIFEST}}
word_pin = hashlib.sha256((SITE / WORD_MANIFEST).read_bytes()).hexdigest()
ready = (qa.get("status") == "PASS" and qa.get("scope") == QA_SCOPE
         and qa.get("contentSourceSha256") == hashlib.sha256((SITE / "content.json").read_bytes()).hexdigest()
         and qa.get("exampleBundleSha256") == e["bundle"]["sha256"]
         and qa.get("walkthroughProvenanceSha256") == walkthrough_pin
         and qa.get("wordReleaseSha256") == word_pin
         and qa.get("validatedFileSha256") == qa_pins
         and privacy.get("status") == "PASS" and privacy.get("scope") == PRIVACY_SCOPE
         and privacy.get("walkthroughProvenanceSha256") == walkthrough_pin
         and privacy.get("historicalImagesReviewed") == 8 and privacy.get("walkthroughImagesReviewed") == 9
         and privacy.get("wordImagesReviewed") == 2 and privacy.get("wordReleaseSha256") == word_pin
         and privacy.get("screenedFileSha256") == privacy_pins)
m = {
    "schemaVersion": "5.0", "status": "READY_FOR_PARENT_PUBLICATION" if ready else "LOCAL_REVIEW_PENDING",
    "scope": PUBLICATION_SCOPE,
    "publicationPerformedBySiteAuthor": False, "runtimeActionsPerformed": False,
    "hosting": c["hosting"], "singleStatusSource": "content.json",
    "example": c["example"], "historicalExample": c["historicalExample"], "approvedArchive": e["bundle"],
    "walkthroughProvenance": walkthrough, "walkthroughProvenanceSha256": walkthrough_pin,
    "followUp": c["followUp"], "followUpProvenance": followup,
    "wordOutputRelease": word, "wordReleaseSha256": word_pin,
    "files": files, "exactPublicRepositoryAllowlist": ALL,
    "exactDeploymentAllowlist": DEPLOY + [MANIFEST], "repositoryOnlyAllowlist": REPOSITORY_ONLY,
    "privacyReport": "PRIVACY-REPORT.json",
    "freshLocalQa": {"status": qa.get("status"), "checksPassed": len(qa.get("cases", [])),
                     "source": "qa/RESULTS.json", "historicalQaInherited": False},
    "manifestSelf": {"path": MANIFEST, "sha256": None, "reason": "The separate final handoff SHA avoids a circular self-hash."},
    "historyPolicy": "Use only this exact reviewed allowlist. Private originals, previous working trees and unrelated publication/QA snapshots are excluded. The explicit historical fourteen-file evidence bundle is retained unchanged.",
}
(SITE / MANIFEST).write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Fresh real-example manifest: {len(ALL)} repository paths; {len(DEPLOY)+1} Pages paths; {m['status']}.")
print("Manifest SHA-256:", hashlib.sha256((SITE / MANIFEST).read_bytes()).hexdigest())
