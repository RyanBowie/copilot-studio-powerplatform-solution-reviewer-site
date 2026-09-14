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
from public_inventory import ALL, IMAGES, WALKTHROUGH_IMAGES, MANIFEST
from prepare_real_example import validate_files
from build_followup import verify as verify_followup
from build_walkthrough import verify as verify_walkthrough, verify_outputs, PROVENANCE as WALKTHROUGH_PROVENANCE, PREFIX as WALKTHROUGH_PREFIX

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


def verify_image_review(review, prefix, names, site=SITE):
    if review.get("visualReviewComplete") is not True or not isinstance(review.get("images"), list):
        raise ValueError("Every image needs a separately supplied, completed hash-bound visual/privacy review.")
    rows = {}
    for row in review["images"]:
        name = row.get("file")
        if name in names:
            name = prefix + "/" + name
        if name in rows or name not in {prefix + "/" + item for item in names}:
            raise ValueError("Unexpected or duplicate image-review path.")
        if not isinstance(row.get("text"), str):
            raise ValueError("Reviewed offline OCR text is required, including an explicit empty string when no text exists.")
        rows[name] = row
    if set(rows) != {prefix + "/" + item for item in names}:
        raise ValueError("Every exact current image must have an independent review pin.")
    for name, row in rows.items():
        data = (Path(site) / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != row.get("sha256"):
            raise ValueError("Image differs from independently reviewed bytes: " + name)
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "PNG" or image.info or getattr(image, "n_frames", 1) != 1:
                raise ValueError("Only metadata-free static PNG pixels may be public.")
            image.load()
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-patterns", type=Path, required=True)
    parser.add_argument("--image-review", type=Path, required=True)
    parser.add_argument("--walkthrough-image-review", type=Path, required=True)
    args = parser.parse_args()
    for path in [args.private_patterns, args.image_review, args.walkthrough_image_review]:
        if not path.resolve().is_relative_to(SITE / "_private-hold") or not path.is_file():
            raise ValueError("Private screening inputs must be existing files under this site's _private-hold.")
    patterns = json.loads(args.private_patterns.read_text(encoding="utf-8-sig"))
    if not isinstance(patterns, list) or not patterns or not all(isinstance(pattern, str) and pattern for pattern in patterns):
        raise ValueError("A nonempty reviewed list of private restriction patterns is required.")
    review = json.loads(args.image_review.read_text(encoding="utf-8-sig"))
    walkthrough_review = json.loads(args.walkthrough_image_review.read_text(encoding="utf-8-sig"))
    e = json.loads((SITE / "downloads/real-canvas-example-manifest.json").read_text(encoding="utf-8"))
    validate_files(e)
    followup = verify_followup()
    walkthrough = verify_walkthrough()
    verify_outputs(walkthrough)
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
    images = verify_image_review(review, "examples/real-canvas", IMAGES)
    images.update(verify_image_review(walkthrough_review, WALKTHROUGH_PREFIX, WALKTHROUGH_IMAGES))
    for name, row in images.items():
        text_check(name + " OCR", row["text"])
    report = {
        "status": "PASS" if not failures else "REVIEW_REQUIRED",
        "scope": "MATCHED_CANVAS_WALKTHROUGH_PUBLIC_TREE",
        "publicRepositoryPaths": len(ALL), "screened": totals, "imagesReviewed": len(images),
        "historicalImagesReviewed": len(IMAGES), "walkthroughImagesReviewed": len(WALKTHROUGH_IMAGES),
        "walkthroughProvenanceSha256": hashlib.sha256((SITE / WALKTHROUGH_PROVENANCE).read_bytes()).hexdigest(),
        "restrictedContextMatches": sum(row["kind"] == "restricted-context" for row in failures),
        "bindingCredentialMetadataMatches": sum(row["kind"] != "restricted-context" for row in failures),
        "screenedFileSha256": {name: hashlib.sha256((SITE / name).read_bytes()).hexdigest()
                              for name in ALL if name not in {"PRIVACY-REPORT.json", MANIFEST}},
        "hashScope": "Exact current public files, not private acceptance records. Generated privacy/publication manifests are text-screened when present and excluded from this map to avoid circular hashes.",
        "privateTermsOrOcrPayloadsPublished": False,
        "imageReview": "Separate supplied private reviews pin all eight historical and all nine matched native image derivatives. The user visually approved the nine matched derivatives; the site author verified pixel masks/crops and offline OCR, not an independent complete visual review. OCR text is screened with the same private patterns; PNGs are decoded and metadata checked. This tool never creates review sign-offs.",
        "bodyPolicy": "All four historical TXT files and eight historical PNGs match their unchanged pins. Separate no-email benchmarks retain their provenance. Every matched authoritative TXT/JSON and PNG matches its reviewed provenance; the full Markdown derivative roundtrips all report bytes.",
        "followUpReport": followup["files"][0],
        "excluded": ["Raw app/solution and private originals/diagnostics", "Mixed Inbox/autoreply images", "Installers, previous examples and previous QA/publication artifacts", "Restricted application evidence and private bindings"],
        "historyPolicy": "Only this exact reviewed allowlist is eligible. Private working directories and unrelated historical trees are never publication inputs.",
        "runtimeActionsPerformed": False,
    }
    (SITE / "PRIVACY-REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if failures:
        (args.image_review.parent / "private-screen-findings.json").write_text(json.dumps(failures, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("Public screening requires review; findings retained privately.")
    print("Approved real-example public screening PASS; no private terms or OCR text published.")


if __name__ == "__main__":
    main()
