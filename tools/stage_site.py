"""Stage only the exact freshly approved real-example tree; no publication action."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath
from public_inventory import ALL, DEPLOY, MANIFEST, LOCAL_DIRECTORIES
from build_walkthrough import verify as verify_walkthrough, verify_outputs, primary_content
from word_release import verify as verify_word_release, PATHS as WORD_PATHS, PUBLICATION_SCOPE
from solution_release import verify as verify_solutions

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--repository", action="store_true")
parser.add_argument("--output", type=Path, help="New private staging directory, for --repository only.")
args = parser.parse_args()
m = json.loads((SITE / MANIFEST).read_text(encoding="utf-8"))
walkthrough = verify_walkthrough()
word = verify_word_release(required=True)
solutions = verify_solutions(required=m.get("solutionImportRelease") is not None, publication=True)
if m.get("solutionImportRelease") != solutions:
    raise SystemExit("Current approved import-first release differs from the publication manifest.")
verify_outputs(walkthrough)
if m["example"] != primary_content(walkthrough):
    raise SystemExit("Manifest does not describe the verified matched walkthrough.")
if m["status"] != "READY_FOR_PARENT_PUBLICATION" or m["scope"] != PUBLICATION_SCOPE or m.get("wordOutputRelease") != word:
    raise SystemExit("Current real-example privacy/QA approval is required.")
if set(m["exactPublicRepositoryAllowlist"]) != set(ALL) or set(m["exactDeploymentAllowlist"]) != set(DEPLOY + [MANIFEST]):
    raise SystemExit("Explicit current inventory differs.")
actual = {p.relative_to(SITE).as_posix() for p in SITE.rglob("*")
          if p.is_file() and not any(part in LOCAL_DIRECTORIES for part in p.relative_to(SITE).parts)}
if actual != set(ALL):
    raise SystemExit("Candidate contains missing/unlisted files.")
if (len(m["files"]) != len(ALL) - 1
        or {row["path"] for row in m["files"]} != set(ALL) - {MANIFEST}):
    raise SystemExit("Manifest pin closure differs from the complete explicit allowlist.")
for row in m["files"]:
    name = row["path"]
    path = SITE.joinpath(*PurePosixPath(name).parts)
    if ".." in PurePosixPath(name).parts or "\\" in name or not path.resolve().is_relative_to(SITE):
        raise SystemExit("Unsafe public path.")
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        raise SystemExit("File pin mismatch: " + name)
    approved_archives = {
        m["approvedArchive"]["path"]: m["approvedArchive"]["sha256"],
        WORD_PATHS["bundle"]: word["files"]["bundle"]["sha256"],
    }
    if solutions:
        approved_archives.update({
            row["path"]: row["sha256"] for row in solutions["files"].values()
            if row["path"].endswith(".zip")
        })
    if path.suffix.lower() == ".zip" and approved_archives.get(name) != row["sha256"]:
        raise SystemExit("Only exact reviewed evidence, Word and import-first solution archives may be staged.")
target = SITE / ("_public-repository" if args.repository else "_site")
if args.output:
    target = (SITE / args.output).resolve()
    if not args.repository or not target.is_relative_to((SITE / "_private-hold").resolve()):
        raise SystemExit("Custom staging must be a new repository directory under _private-hold.")
if target.exists():
    raise SystemExit("Staging already exists; inspect rather than overwrite.")
selected = ALL if args.repository else DEPLOY + [MANIFEST]
target.mkdir()
for name in selected:
    dest = target.joinpath(*PurePosixPath(name).parts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SITE / name, dest)
print(f"Staged {len(selected)} exact current public paths. No GitHub or runtime action.")
