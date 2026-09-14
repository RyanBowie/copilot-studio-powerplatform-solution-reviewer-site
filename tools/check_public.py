"""Scope-bound public screening; private restriction patterns/visual records stay private."""
import argparse
import base64
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZipFile
from PIL import Image
from public_inventory import ALL, IMAGES, MANIFEST
from prepare_real_example import validate_files
from build_followup import verify as verify_followup

SITE = Path(__file__).resolve().parents[1]
GENERIC = [
    r"https?://[^\s<>\"')]*\.sharepoint\.com",
    r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:[A-Za-z]{2,}|xn--[A-Za-z0-9-]{2,})",
    r"(?i)[?&](?:sig|token|client_secret|access_token)=[^<>\s\"']+",
    r"(?i)https?://[^\s\"']*(?:logic\.azure\.com|api\.powerplatform\.com|crm\d*\.dynamics\.com)",
    r"(?i)[A-Z]:[\\/]+Users[\\/]+[^<>\s\"']+",
    r"(?i)Bearer\s+[A-Za-z0-9._~-]{12,}",
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-patterns", type=Path, required=True)
    parser.add_argument("--image-review", type=Path, required=True)
    args = parser.parse_args()
    patterns = json.loads(args.private_patterns.read_text(encoding="utf-8-sig"))
    review = json.loads(args.image_review.read_text(encoding="utf-8-sig"))
    e = json.loads((SITE / "downloads/real-canvas-example-manifest.json").read_text(encoding="utf-8"))
    validate_files(e)
    followup = verify_followup()
    failures = []
    totals = {"textMembers": 0, "archives": 0, "decodedCandidates": 0}

    def text_check(label, value):
        totals["textMembers"] += 1
        variants = [value, unquote(value)]
        if "\\u" in value:
            variants.append(re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), value))
        for candidate in re.findall(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{40,}={0,2}", value):
            if len(candidate) % 4 == 0:
                try:
                    decoded = base64.b64decode(candidate, validate=True).decode("utf-8")
                    if decoded.isprintable():
                        variants.append(decoded)
                        totals["decodedCandidates"] += 1
                except (ValueError, UnicodeDecodeError):
                    pass
        for text in variants:
            if any(re.search(pattern, text, re.I) for pattern in patterns):
                failures.append({"kind": "restricted-context", "publicMember": label})
            if any(re.search(pattern, text, re.I) for pattern in GENERIC):
                failures.append({"kind": "binding-credential-like", "publicMember": label})

    def inspect(label, data, depth=0):
        if depth > 4:
            raise ValueError("Unexpected archive nesting.")
        if label.endswith(".zip"):
            totals["archives"] += 1
            with ZipFile(io.BytesIO(data)) as archive:
                if sum(row.file_size for row in archive.infolist()) > 50 * 1024 * 1024:
                    raise ValueError("Unexpected archive expansion.")
                for row in archive.infolist():
                    if not row.is_dir():
                        inspect(label + "::" + row.filename, archive.read(row.filename), depth + 1)
        elif not label.endswith(".png"):
            text_check(label, data.decode("utf-8-sig"))

    for name in ALL:
        if name not in {"PRIVACY-REPORT.json", MANIFEST}:
            inspect(name, (SITE / name).read_bytes())
    for name in ["PRIVACY-REPORT.json", MANIFEST]:
        if (SITE / name).exists():
            text_check(name, (SITE / name).read_text(encoding="utf-8-sig"))
    images = {row["file"]: row for row in review["images"]}
    if set(images) != set(IMAGES) or not review["visualReviewComplete"]:
        raise ValueError("Every current approved image needs hash-bound visual review.")
    for name in IMAGES:
        path = SITE / "examples/real-canvas" / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != images[name]["sha256"]:
            raise ValueError("Image differs from reviewed bytes.")
        with Image.open(path) as image:
            if image.info:
                failures.append({"kind": "image-metadata", "publicMember": name})
        text_check(name + " OCR", images[name]["text"])
    report = {
        "status": "PASS" if not failures else "REVIEW_REQUIRED",
        "scope": "APPROVED_REAL_CANVAS_PUBLIC_TREE",
        "publicRepositoryPaths": len(ALL), "screened": totals, "imagesReviewed": len(IMAGES),
        "restrictedContextMatches": sum(row["kind"] == "restricted-context" for row in failures),
        "bindingCredentialMetadataMatches": sum(row["kind"] != "restricted-context" for row in failures),
        "screenedFileSha256": {name: hashlib.sha256((SITE / name).read_bytes()).hexdigest()
                              for name in ALL if name not in {"PRIVACY-REPORT.json", MANIFEST}},
        "hashScope": "Exact current public files, not private acceptance records. Generated privacy/publication manifests are text-screened when present and excluded from this map to avoid circular hashes.",
        "privateTermsOrOcrPayloadsPublished": False,
        "imageReview": "Normal site-author visual/privacy review of eight exact approved derivatives, assisted by offline OCR. Original-to-derivative pixel comparison is Test-reported, not independently repeated by the site author. Four images are user-provided, not TEST captures.",
        "bodyPolicy": "All four historical TXT files and all eight PNGs match approved input bytes. The separately reviewed complete follow-up MAIN and identity-free measurements match their own public provenance pins.",
        "followUpReport": followup["files"][0],
        "excluded": ["Raw app/solution and private originals/diagnostics", "Mixed Inbox/autoreply images", "Installers, previous examples and previous QA/publication artifacts", "Restricted application evidence and private bindings"],
        "historyPolicy": "Only a new clean repository/history may publish this exact current allowlist.",
        "runtimeActionsPerformed": False,
    }
    (SITE / "PRIVACY-REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if failures:
        (args.image_review.parent / "private-screen-findings.json").write_text(json.dumps(failures, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("Public screening requires review; findings retained privately.")
    print("Approved real-example public screening PASS; no private terms or OCR text published.")


if __name__ == "__main__":
    main()
