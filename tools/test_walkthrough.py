"""Offline validator tests. All synthetic fixtures stay private and are deleted."""
import copy
from html.parser import HTMLParser
import json
import shutil
import struct
import unittest
import uuid
import zlib

import build_walkthrough as w
from build_home import build
from check_public import verify_image_review
from prepare_real_example import validate_files


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def private_test_png():
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00" + b"\xff" * 6 + b"\x00" + b"\xff" * 6)) + chunk(b"IEND", b""))


class ReportText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.reports, self.key, self.depth = {}, None, 0

    def handle_starttag(self, tag, attrs):
        if self.key:
            self.depth += 1
        else:
            key = dict(attrs).get("data-walkthrough-text")
            if key:
                self.key, self.depth = key, 1
                self.reports[key] = ""

    def handle_endtag(self, tag):
        if self.key:
            self.depth -= 1
            if self.depth == 0:
                self.key = None

    def handle_data(self, data):
        if self.key:
            self.reports[self.key] += data


class WalkthroughTests(unittest.TestCase):
    def setUp(self):
        self.site = w.SITE / "_private-hold" / ("walkthrough-unit-" + uuid.uuid4().hex)
        self.directory = self.site / w.PREFIX
        self.directory.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(self.site))
        (self.site / "index.html").write_bytes((w.SITE / "index.html").read_bytes())
        self.p = {
            "schemaVersion": 1, "kind": "REVIEWED_GENUINE_CANVAS_EMAIL_WALKTHROUGH",
            "approvedPublicDerivatives": True, "sourceDisplayName": "Data Entry Testing",
            "revision": "3.3.2.5", "outcome": "ReviewPartial", "accepted": 3, "selected": 5,
            "unavailable": 2, "acceptedPassIds": ["C1", "C3", "C4"], "logicalAgentInvocations": 8,
            "mainValid": True, "screenLinesSupplied": 326, "totalScreenLines": 326,
            "latestScreenCitation": 285, "allFiveSelectedSourcesComplete": True,
            "email": {"nativeSendStatus": "Succeeded", "ownerInboxReceiptVerified": True,
                      "expectedReportLinkVerified": True, "forwardedCorporateReceiptVerified": False,
                      "controlsRestored": True},
            "images": [], "reports": [],
        }
        for role, name in w.IMAGE_ROLES.items():
            data = private_test_png()
            (self.directory / name).write_bytes(data)
            self.p["images"].append({"file": name, "role": role, "bytes": len(data), "sha256": w.sha(data),
                                     "alt": "PRIVATE SYNTHETIC UNIT FIXTURE, NOT REVIEW EVIDENCE",
                                     "caption": "PRIVATE SYNTHETIC VALIDATOR TEST ONLY, NOT A NATIVE CAPTURE"})
        main = "\ufeff" + "".join(
            f"{i}. PRIVATE UNIT TEST section {i}\r\n" + ("All complete canonical test records remain here; NOT RUN.\r\n" * 90)
            for i in range(1, 11)
        ) + "FULL TEST FOOTER\r\n<script>notExecutable()</script> & <tag>\r\n`````\r\nNo final newline"
        bodies = {"MAIN.txt": main.encode("utf-8"), "C1.txt": b"PRIVATE test C1\n",
                  "C3.txt": b"PRIVATE test C3\r\n", "C4.txt": "PRIVATE test C4 café\n```\n".encode("utf-8"),
                  "inventory.json": b'{"privateUnitFixture":"complete inventory"}\r\n',
                  "coverage.json": b'{"privateUnitFixture":"complete coverage, omissions, NOT RUN"}'}
        for name, data in bodies.items():
            self.add_report(name, data, w.BASE_REPORTS.get(name, "component"))
        self.save()

    def add_report(self, name, data, role):
        (self.directory / name).write_bytes(data)
        self.p["reports"].append({"file": name, "role": role, "bytes": len(data), "sha256": w.sha(data)})

    def save(self):
        (self.site / w.PROVENANCE).write_text(json.dumps(self.p, indent=2), encoding="utf-8")

    def assert_invalid(self, field, value):
        self.p[field] = value
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_complete_private_fixture_is_accepted(self):
        self.assertEqual(w.verify(self.site), self.p)

    def test_missing_input_fails_without_writes(self):
        (self.site / w.PROVENANCE).unlink()
        with self.assertRaisesRegex(ValueError, "missing reviewed"):
            w.verify(self.site)
        self.assertFalse((self.site / w.READER).exists())
        self.assertFalse((self.site / w.MARKDOWN).exists())

    def test_real_booleans_not_truthy_strings(self):
        for field in ["approvedPublicDerivatives", "mainValid", "allFiveSelectedSourcesComplete"]:
            for invalid in ["true", 1, False, None]:
                with self.subTest(field=field, value=invalid):
                    self.assert_invalid(field, invalid)
            self.p[field] = True

    def test_every_email_proof_is_required(self):
        for field in ["ownerInboxReceiptVerified", "expectedReportLinkVerified", "controlsRestored"]:
            for invalid in [False, "true", 1]:
                with self.subTest(field=field, value=invalid):
                    self.p["email"][field] = invalid
                    self.save()
                    with self.assertRaises(ValueError):
                        w.verify(self.site)
            self.p["email"][field] = True

    def test_unestablished_corporate_receipt_not_upgraded(self):
        self.p["email"]["forwardedCorporateReceiptVerified"] = True
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_failed_native_send_is_not_receipt(self):
        self.p["email"]["nativeSendStatus"] = "Failed"
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_pending_or_historical_outcome_rejected(self):
        self.assert_invalid("outcome", "Running")
        self.assert_invalid("accepted", 1)

    def test_count_invariant(self):
        self.assert_invalid("unavailable", 1)
        self.p["unavailable"] = 2
        self.assert_invalid("selected", 6)

    def test_counts_and_citations_are_bounded_integers(self):
        for field, values in {"schemaVersion": [True], "accepted": [True, 2, 6, "3"],
                              "logicalAgentInvocations": [0, 14, True], "latestScreenCitation": [0, 327, "285"],
                              "screenLinesSupplied": [80], "totalScreenLines": [400]}.items():
            original = self.p[field]
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_invalid(field, value)
            self.p[field] = original

    def test_source_revision_fixed_to_actual_scope(self):
        self.assert_invalid("sourceDisplayName", "Different source")
        self.p["sourceDisplayName"] = "Data Entry Testing"
        self.assert_invalid("revision", "3.3.1.3")

    def test_duplicate_and_unknown_pass_ids_fail(self):
        for ids in [["C1", "C1", "C4"], ["C1", "C3", "C6"], ["C1", "C2", "C3"], ["C4"]]:
            with self.subTest(ids=ids):
                self.assert_invalid("acceptedPassIds", ids)

    def test_actual_four_of_five_is_rendered_not_hardcoded(self):
        self.p.update(accepted=4, unavailable=1, acceptedPassIds=["C1", "C2", "C3", "C4"])
        self.add_report("C2.txt", b"PRIVATE complete accepted C2 test\n", "component")
        self.save()
        p = w.verify(self.site)
        self.assertEqual(w.primary_content(p)["accepted"], 4)
        self.assertEqual(w.primary_content(p)["acceptedPassIds"], ["C1", "C2", "C3", "C4"])
        self.assertTrue(w.primary_content(p)["combinedTarget"]["achieved"])
        self.assertIn("4/5", w.reader(p, self.site))
        self.assertIn("4 / 5", build(p, self.site))
        for rendered in [build(p, self.site), w.reader(p, self.site), w.markdown(p, self.site)]:
            self.assertIn(w.combined_target(p)["summary"], rendered)
            self.assertIn("achieved in this ONE matched run: 4/5", rendered)
            self.assertIn("does not demonstrate repeated at-least-4/5 performance or 90%", rendered)
        self.assertIn('data-walkthrough-text="C2.txt"', w.reader(p, self.site))
        self.assertIn("C2.txt", w.extract_markdown(w.markdown(p, self.site)))
        self.assertEqual(len(w.documents(p)), 7)

    def test_combined_target_last_quarter_boundary(self):
        self.p.update(accepted=4, unavailable=1, acceptedPassIds=["C1", "C2", "C3", "C4"])
        self.add_report("C2.txt", b"PRIVATE complete accepted C2 test\n", "component")
        for citation, expected in [(244, False), (245, True), (326, True)]:
            with self.subTest(citation=citation):
                self.p["latestScreenCitation"] = citation
                self.save()
                p = w.verify(self.site)
                target = w.combined_target(p)
                self.assertIs(target["achieved"], expected)
                self.assertEqual(target["lastQuarterStartLine"], 245)
                self.assertEqual(target["scope"], "ONE_MATCHED_RUN_ONLY")
                for rendered in [build(p, self.site), w.reader(p, self.site), w.markdown(p, self.site)]:
                    self.assertIn(target["summary"], rendered)
                if not expected:
                    self.assertIn("not established for this matched run", target["summary"])
                    self.assertNotIn("achieved in this ONE matched run", build(p, self.site))

    def test_combined_target_requires_every_evidence_condition(self):
        ready = dict(self.p, accepted=4, unavailable=1, acceptedPassIds=["C1", "C2", "C3", "C4"])
        self.assertTrue(w.combined_target(ready)["achieved"])
        for field, value in [
            ("accepted", 3), ("selected", 4), ("mainValid", False), ("mainValid", "true"),
            ("allFiveSelectedSourcesComplete", False), ("allFiveSelectedSourcesComplete", "true"),
            ("acceptedPassIds", ["C1", "C2", "C3", "C5"]), ("screenLinesSupplied", 80),
            ("latestScreenCitation", 244), ("latestScreenCitation", 327),
        ]:
            with self.subTest(field=field, value=value):
                candidate = dict(ready, **{field: value})
                self.assertFalse(w.combined_target(candidate)["achieved"])
                self.assertIn("not established", w.combined_target(candidate)["summary"])

    def test_extra_private_provenance_field_rejected(self):
        self.p["privateRunId"] = "not permitted"
        self.save()
        with self.assertRaisesRegex(ValueError, "keys differ"):
            w.verify(self.site)

    def test_duplicate_json_keys_rejected(self):
        path = self.site / w.PROVENANCE
        path.write_text(path.read_text(encoding="utf-8").replace('"schemaVersion": 1', '"schemaVersion": 1, "schemaVersion": 1'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            w.verify(self.site)

    def test_every_image_required(self):
        self.p["images"].pop()
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_role_and_filename_mapping_is_explicit(self):
        self.p["images"][0]["role"] = "email"
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_no_path_traversal(self):
        self.p["images"][0]["file"] = "../native-upload-menu.png"
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_extra_raw_files_rejected(self):
        (self.directory / "unreviewed-source.txt").write_text("PRIVATE unit fixture", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unlisted"):
            w.verify(self.site)

    def test_reviewed_bytes_cannot_be_rewritten(self):
        (self.directory / "MAIN.txt").write_text("shortened", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "pin differs"):
            w.verify(self.site)

    def test_all_ten_main_sections_required(self):
        row = next(row for row in self.p["reports"] if row["file"] == "MAIN.txt")
        data = (self.directory / row["file"]).read_bytes().replace(b"10. PRIVATE UNIT TEST", b"Missing section")
        (self.directory / row["file"]).write_bytes(data)
        row.update(bytes=len(data), sha256=w.sha(data))
        self.save()
        with self.assertRaisesRegex(ValueError, "ten ordered"):
            w.verify(self.site)

    def test_metadata_and_trailing_payload_rejected(self):
        data = private_test_png()
        for invalid in [data[:-12] + chunk(b"tEXt", b"private\x00metadata") + data[-12:], data + b"extra"]:
            with self.assertRaises(ValueError):
                w.png_dimensions(invalid)

    def test_alt_and_caption_are_plain_text(self):
        self.p["images"][0]["caption"] = '<script>unreviewed()</script>'
        self.save()
        with self.assertRaises(ValueError):
            w.verify(self.site)

    def test_lossless_markdown_full_large_report(self):
        expected = {row["file"]: (self.directory / row["file"]).read_bytes() for row in self.p["reports"]}
        self.assertGreater(len(expected["MAIN.txt"]), 43000)
        value = w.markdown(self.p, self.site)
        self.assertEqual(w.extract_markdown(value), expected)
        self.assertIn("Presentation-only full derivative", value)
        with self.assertRaisesRegex(ValueError, "not lossless"):
            w.extract_markdown(value.replace("FULL TEST FOOTER", "SHORT TEST FOOTER"))

    def test_html_is_complete_escaped_and_not_fetch_dependent(self):
        source = w.reader(self.p, self.site)
        parser = ReportText()
        parser.feed(source)
        expected = {row["file"]: w.normalized_text((self.directory / row["file"]).read_bytes()) for row in self.p["reports"]}
        self.assertEqual(parser.reports, expected)
        self.assertNotIn("<script>notExecutable()", source)
        self.assertIn("&lt;script&gt;notExecutable()", source)
        self.assertEqual(source.count('id="main-section-'), 10)
        self.assertEqual(source.count('<li><a href="#main-section-'), 10)
        self.assertNotIn("fetch(", source)
        self.assertIn("--cp-bg:", source)
        self.assertIn('data-theme="dark"', source)

    def test_stale_generated_outputs_rejected(self):
        (self.site / w.MARKDOWN).write_bytes(w.markdown(self.p, self.site).encode("utf-8"))
        (self.site / w.READER).write_bytes(w.reader(self.p, self.site).encode("utf-8"))
        w.verify_outputs(self.p, self.site)
        (self.site / w.MARKDOWN).write_text("summary only", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing or stale"):
            w.verify_outputs(self.p, self.site)

    def test_homepage_primary_and_idempotence(self):
        value = build(self.p, self.site)
        self.assertIn('data-full-example-link href="walkthrough.html"', value)
        self.assertEqual(value.count('<figure class="screenshot"'), 9)
        primary = value.split('<section class="section wrap" id="history">')[0]
        self.assertNotIn("1/5", primary)
        self.assertNotIn("80/326", primary)
        self.assertNotIn("not verified Inbox receipt", primary)
        self.assertIn("3 / 5", primary)
        self.assertIn("326 / 326", primary)
        self.assertIn("GPT5Chat", value)
        self.assertIn("All 11 historical results", value)
        (self.site / "index.html").write_bytes(value.encode("utf-8"))
        self.assertEqual(build(self.p, self.site), value)

    def test_independent_image_review_is_required(self):
        review = {"visualReviewComplete": True, "images": [
            {"file": row["file"], "sha256": row["sha256"], "text": "PRIVATE SYNTHETIC UNIT TEST OCR ONLY"}
            for row in self.p["images"]
        ]}
        self.assertEqual(len(verify_image_review(review, w.PREFIX, list(w.IMAGE_ROLES.values()), self.site)), 9)
        for change in ["not-complete", "duplicate", "missing", "wrong-pin", "missing-ocr"]:
            changed = copy.deepcopy(review)
            if change == "not-complete":
                changed["visualReviewComplete"] = "true"
            elif change == "duplicate":
                changed["images"].append(changed["images"][0])
            elif change == "missing":
                changed["images"].pop()
            elif change == "wrong-pin":
                changed["images"][0]["sha256"] = "0" * 64
            else:
                del changed["images"][0]["text"]
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_image_review(changed, w.PREFIX, list(w.IMAGE_ROLES.values()), self.site)

    def test_historical_immutable_bundle_still_verifies(self):
        manifest = json.loads((w.SITE / "downloads/real-canvas-example-manifest.json").read_text(encoding="utf-8"))
        validate_files(manifest)
        self.assertEqual(w.sha((w.SITE / manifest["bundle"]["path"]).read_bytes()), manifest["bundle"]["sha256"])


if __name__ == "__main__":
    unittest.main()
