"""Stage exact local solution candidates; never import, activate, or approve publication."""
import argparse
import json
from pathlib import Path
import re
import tempfile

import solution_release as release
from word_release import archive_members, identifier_members, text_variants, verify as verify_word
from check_public import GENERIC, binding_screen_text


def screen(contents, private_patterns, known_structural):
    occurrences = identifier_members(contents, paths=release.PATHS, roles=release.PATHS)
    identifiers = sorted({value for values in occurrences.values() for value in values})
    if not set(identifiers) <= known_structural:
        raise ValueError("New identifiers need independent classification before public staging.")
    inspected = 0

    def inspect(label, data, depth=0):
        nonlocal inspected
        if depth > 4:
            raise ValueError("Unexpected nested candidate archive depth.")
        inspected += 1
        if label.lower().endswith((".zip", ".docx")):
            for name, value in archive_members(data).items():
                inspect(label + "::" + name, value, depth + 1)
        else:
            for text in text_variants(data.decode("utf-8-sig")):
                if any(pattern.casefold() in text.casefold() for pattern in private_patterns):
                    raise ValueError("Private-source pattern in candidate member: " + label)
                if any(re.search(pattern, binding_screen_text(text), re.I) for pattern in GENERIC[:-1]):
                    raise ValueError("Credential or target binding requires review: " + label)

    for role, value in contents.items():
        inspect(release.PATHS[role], value)
    return occurrences, identifiers, inspected


def prepare(source, private_audit, native_evidence=None):
    source = source.resolve()
    if not source.is_relative_to(release.SITE / "_private-hold"):
        raise ValueError("Candidate input must be in this worktree's private holding directory.")
    audit = json.loads(private_audit.read_text(encoding="utf-8-sig"))
    patterns = audit.get("privatePatternSet")
    if not isinstance(patterns, list) or not patterns or not all(isinstance(p, str) and p for p in patterns):
        raise ValueError("The exact original private-source pattern inventory is required.")
    contents = {role: (source / Path(name).name).read_bytes()
                for role, name in release.PATHS.items() if role != "setup"}
    support = archive_members(contents["support"])
    contents["setup"] = support["INSTALL.md"]
    for role in ("reviewer", "automation"):
        release.verify_solution(contents[role], role)
    historical = verify_word(required=True)
    occurrences, identifiers, inspected = screen(contents, patterns, set(historical["structuralIdentifiers"]))
    native = json.loads(native_evidence.read_text(encoding="utf-8-sig")) if native_evidence else []
    manifest = {
        "schemaVersion": 1, "kind": "IMPORT_FIRST_UNMANAGED_SOLUTION_RELEASE",
        "version": release.VERSION, "approvedPublicDistribution": False,
        "evidence": {
            "sameTenantSandboxImportVerified": bool(native),
            "automaticWordRuntimeVerified": False, "crossTenantInstallationVerified": False,
            "separateLeastPrivilegeRequesterVerified": False, "publishedDemoAgentChanged": False,
            "setupOrActivationPerformed": False,
        },
        "files": {
            role: {"path": release.PATHS[role], "bytes": len(value), "sha256": release.sha(value)}
            for role, value in contents.items()
        },
        "archiveMembers": {
            role: {name: {"bytes": len(value), "sha256": release.sha(value)} for name, value in archive_members(data).items()}
            for role, data in contents.items() if role != "setup"
        },
        "structuralIdentifiers": identifiers, "structuralIdentifierMembers": occurrences,
        "nativeImports": native,
        "source": {
            "historicalDistributionVersion": "3.3.2.6",
            "nativeReviewerArchiveSha256": "6ffe125f8459b2ec343cf1a31a8f2e41e0cad8d72a5be46b83daa2c565d39c50",
            "nativeAutomationArchiveSha256": "7eccd5c7c64ea7472de908f7e97ea7d08ba03a4bc1742a956f74993914d735b3",
            "automaticOverlaySha256": "acea5101fb52bf4a00af86ba51c5e14631b142b9c6177ae72b19da2c10b428b6",
            "automaticOverlayNativeRuntimeAccepted": False,
        },
        "localScreening": {
            "expandedParts": inspected, "privateSourcePatterns": len(patterns),
            "privateSourceMatches": 0, "targetBindingMatches": 0,
            "parentPublicSafetyApproval": False,
        },
    }
    for role, value in contents.items():
        target = release.SITE / release.PATHS[role]
        if target.exists() and target.read_bytes() != value:
            raise ValueError("Existing public candidate differs; do not overwrite it: " + str(target))
    manifest_path = release.SITE / release.MANIFEST
    if manifest_path.exists():
        raise ValueError("The import-release manifest already exists; review it rather than overwrite.")
    serialized = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="irv-", dir=release.SITE / "_private-hold") as temporary:
        verification = Path(temporary)
        for role, value in contents.items():
            target = verification / release.PATHS[role]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(value)
        (verification / release.MANIFEST).write_bytes(serialized)
        release.verify(verification, required=True)
    for role, value in contents.items():
        (release.SITE / release.PATHS[role]).write_bytes(value)
    manifest_path.write_bytes(serialized)
    release.verify(release.SITE, required=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--private-audit", type=Path, required=True)
    parser.add_argument("--native-evidence", type=Path)
    args = parser.parse_args()
    result = prepare(args.source, args.private_audit, args.native_evidence)
    print("Exact candidate downloads prepared; parent publication approval remains false.")
    for role, row in result["files"].items():
        print(role, row["path"], row["sha256"])
