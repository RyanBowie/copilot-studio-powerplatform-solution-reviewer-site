"""Explicit historical and reviewed matched-run paths; no wildcard publication."""
from build_walkthrough import SITE, PREFIX, PROVENANCE as WALKTHROUGH_PROVENANCE, MARKDOWN, READER, IMAGE_ROLES, verify
from word_release import PUBLIC_PATHS as WORD_PATHS

WALKTHROUGH_IMAGES = list(IMAGE_ROLES.values())
# Missing input declares paths only, never an outcome. All publication tools verify first.
WALKTHROUGH_REPORTS = ([row["file"] for row in verify()["reports"]] if (SITE / WALKTHROUGH_PROVENANCE).is_file()
                       else ["MAIN.txt", "C1.txt", "C3.txt", "C4.txt", "inventory.json", "coverage.json"])
IMAGES = [
    "native-upload-menu-before-selection.png", "native-upload-file-row-confirmed.png",
    "actual-result-review-txt.png", "actual-result-C4-txt.png", "user-provided-notification-body.png",
    "user-provided-main-opening.png", "user-provided-main-assessment-findings.png",
    "user-provided-main-verification-omissions.png",
]
REPORTS = ["real-canvas-MAIN.txt", "real-canvas-C4.txt", "real-canvas-inventory.txt", "real-canvas-coverage.txt"]
PROVENANCE = ["public-provenance.json", "user-capture-provenance.v1.json"]
DEPLOY = [
    "index.html", "site.css", "layout.css", "site.js", "example.css", "example.js", "full-example.html",
    "content.json", "content.js", "reference.js", "README.md", "reference/agent-instructions.txt",
    "reference/topic-tool-source.json", "downloads/real-canvas-example-manifest.json",
    "downloads/real-canvas-review-example.zip", "PRIVACY-REPORT.json", ".nojekyll",
    "follow-up.html", "examples/follow-up/results.json", "examples/follow-up/complete-review.txt",
    "examples/follow-up/provenance.json",
] + ["examples/real-canvas/" + name for name in IMAGES + REPORTS + PROVENANCE] + [
    READER, WALKTHROUGH_PROVENANCE, MARKDOWN,
] + [PREFIX + "/" + name for name in WALKTHROUGH_IMAGES + WALKTHROUGH_REPORTS] + WORD_PATHS
REPOSITORY_ONLY = [
    ".gitignore", ".gitattributes", ".github/workflows/pages.yml", "qa/RESULTS.json",
    "tools/build_home.py", "tools/generate_content.py", "tools/prepare_real_example.py",
    "tools/public_inventory.py", "tools/check_public.py", "tools/qa_site.py",
    "tools/make_manifest.py", "tools/stage_site.py", "tools/serve_preview.py",
    "tools/build_followup.py", "tools/build_walkthrough.py", "tools/test_walkthrough.py",
    "tools/word_release.py", "tools/test_word_release.py",
]
MANIFEST = "PUBLICATION-MANIFEST.json"
ALL = DEPLOY + REPOSITORY_ONLY + [MANIFEST]
LOCAL_DIRECTORIES = {"_private-hold", "_public-repository", "_site", ".qa-work", "__pycache__", ".git"}
