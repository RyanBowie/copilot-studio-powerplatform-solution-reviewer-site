"""Fresh local QA for the approved real example; no prior results or runtime calls."""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile
from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
from public_inventory import IMAGES, WALKTHROUGH_IMAGES, DEPLOY, ALL, MANIFEST
from prepare_real_example import validate_files, DOCUMENTS, TEXT_PINS, render_text
from build_followup import verify as verify_followup
from build_walkthrough import (
    verify as verify_walkthrough, verify_outputs, documents as walkthrough_documents,
    normalized_text, extract_markdown, primary_content, combined_target, PREFIX as WALKTHROUGH_PREFIX,
    PROVENANCE as WALKTHROUGH_PROVENANCE, MARKDOWN, IMAGE_ROLES,
)
from word_release import verify as verify_word_release, summary as word_summary, MANIFEST as WORD_MANIFEST, PATHS as WORD_PATHS, QA_SCOPE
from solution_release import verify as verify_solutions, MANIFEST as SOLUTION_MANIFEST, PATHS as SOLUTION_PATHS

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:4178/preview/")
parser.add_argument("--capture-directory", type=Path, required=True)
args = parser.parse_args()
captures = args.capture_directory.resolve()
if urlparse(args.base_url).hostname != "127.0.0.1" or not captures.is_relative_to(SITE / "_private-hold"):
    raise SystemExit("Only a local preview and owned private capture directory are allowed.")
walkthrough = verify_walkthrough()
word = verify_word_release(required=True)
solutions = verify_solutions()
verify_outputs(walkthrough)
walkthrough_rows = walkthrough_documents(walkthrough)
target_status = combined_target(walkthrough)
expected_target = (
    walkthrough["accepted"] >= 4 and walkthrough["selected"] == 5
    and walkthrough["mainValid"] is True and walkthrough["allFiveSelectedSourcesComplete"] is True
    and "C4" in walkthrough["acceptedPassIds"]
    and walkthrough["screenLinesSupplied"] == walkthrough["totalScreenLines"]
    and 3 * walkthrough["totalScreenLines"] < 4 * walkthrough["latestScreenCitation"] <= 4 * walkthrough["totalScreenLines"]
)
if captures.exists():
    raise SystemExit("Capture directory exists; do not overwrite.")
captures.mkdir(parents=True)
storage = SITE / ".qa-work"
if storage.exists():
    raise SystemExit("Browser storage exists; inspect before retrying.")
storage.mkdir()
(storage / "owned-by-real-qa").write_text("Fresh real-example local QA only.\n", encoding="utf-8")
os.environ["TEMP"] = os.environ["TMP"] = str(storage)
tempfile.tempdir = str(storage)
c = json.loads((SITE / "content.json").read_text(encoding="utf-8"))
e = json.loads((SITE / "downloads/real-canvas-example-manifest.json").read_text(encoding="utf-8"))
result = {"status": "PENDING", "scope": QA_SCOPE,
          "historicalQaInherited": False, "runtimeActionsPerformed": False, "capturesPublished": False,
          "contentSourceSha256": hashlib.sha256((SITE / "content.json").read_bytes()).hexdigest(),
          "exampleBundleSha256": e["bundle"]["sha256"],
          "walkthroughProvenanceSha256": hashlib.sha256((SITE / WALKTHROUGH_PROVENANCE).read_bytes()).hexdigest(),
          "wordReleaseSha256": hashlib.sha256((SITE / WORD_MANIFEST).read_bytes()).hexdigest(),
          "solutionImportReleaseSha256": hashlib.sha256((SITE / SOLUTION_MANIFEST).read_bytes()).hexdigest() if solutions else None,
          "validatedFileSha256": {name: hashlib.sha256((SITE / name).read_bytes()).hexdigest()
                                 for name in ALL if name not in {"qa/RESULTS.json", "PRIVACY-REPORT.json", MANIFEST}},
          "cases": [], "externalRequests": [], "errors": []}


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    result["cases"].append({"check": label, "result": "PASS"})


def capture(page, name):
    page.evaluate("""() => {
      let n=document.getElementById('local-qa-label');
      if(!n){n=document.createElement('div');n.id='local-qa-label';document.body.prepend(n);}
      n.textContent='LOCAL WEBSITE PREVIEW · approved real-review derivatives, not a new runtime capture';
      n.style.cssText='background:var(--cp-accent);color:var(--cp-accent-fg);font:600 12px "Segoe UI",sans-serif;padding:8px 20px';
      if(scrollY>0)n.style.cssText+=';position:fixed;top:0;left:0;right:0;z-index:100';
    }""")
    page.screenshot(path=str(captures / name))


def compact(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


LIGHT_PALETTE = dict(zip(
    ("bg", "bg-elevated", "surface", "surface-soft", "border", "border-strong",
     "text", "text-muted", "text-soft", "accent", "accent-hover", "accent-soft",
     "accent-fg", "link", "success", "danger", "warning", "chart-blue",
     "chart-indigo", "chart-purple", "chart-violet", "chart-magenta", "chart-track"),
    ("#f2f2f8", "#f8f7fc", "#ffffff", "#f2f2f8", "#e3dfed", "#9285aa",
     "#102631", "#52637a", "#667287", "#7653ae", "#58378b", "#eee8f7",
     "#ffffff", "#066bc7", "#207346", "#b4233e", "#8c6208", "#0877dd",
     "#5364ba", "#7653ae", "#9651bb", "#b535c3", "#e8e3f0"),
    strict=True,
))
DARK_PALETTE = dict(zip(
    LIGHT_PALETTE,
    ("#171717", "#222222", "#1f1f1f", "#262626", "#3b3b3b", "#858585",
     "#f2f2f2", "#bdbdbd", "#aaaaaa", "#c3a0ef", "#debeff", "#2b2b2b",
     "#181818", "#80baff", "#4ade80", "#f87171", "#fbbf24", "#69aeff",
     "#98a5ff", "#bc98ed", "#d097ee", "#ed8fea", "#3b3b3b"),
    strict=True,
))


def check_theme(page, theme, label):
    expected = LIGHT_PALETTE if theme == "light" else DARK_PALETTE
    actual = page.evaluate("""names => {
      const root = getComputedStyle(document.documentElement);
      return Object.fromEntries(names.map(name => [name, root.getPropertyValue('--cp-' + name).trim()]));
    }""", list(expected))
    check(actual == expected, label + ": effective benchmark palette, including semantic status colors")
    check(page.locator("html").get_attribute("data-theme") == theme, label + ": selected theme")
    style = page.locator("h1").evaluate("""node => {
      const title = getComputedStyle(node), body = getComputedStyle(document.body);
      return {weight: title.fontWeight, size: parseFloat(title.fontSize),
        line: parseFloat(title.lineHeight), spacing: parseFloat(title.letterSpacing),
        gradient: title.backgroundImage, color: title.color,
        spansInherit: [...node.querySelectorAll('span')].every(n => getComputedStyle(n).color === title.color),
        bodySize: body.fontSize, bodyLine: body.lineHeight, font: body.fontFamily};
    }""")
    check(style["weight"] == "450" and abs(style["line"] / style["size"] - 1.12) < .001
          and abs(style["spacing"] / style["size"] + .035) < .001,
          label + ": lightweight editorial hero typography")
    rgb = lambda value: "rgb(" + ", ".join(str(int(value[i:i + 2], 16)) for i in (1, 3, 5)) + ")"
    check(style["gradient"] == "linear-gradient(105deg, " + rgb(expected["chart-blue"]) + ", "
          + rgb(expected["chart-purple"]) + " 56%, " + rgb(expected["chart-magenta"]) + ")"
          and style["color"] == "rgba(0, 0, 0, 0)" and style["spansInherit"],
          label + ": blue-purple-magenta hero text, including nested spans")
    check(style["bodySize"] == "16px" and style["bodyLine"] == "26.4px"
          and style["font"].startswith('"Segoe UI", Aptos, Calibri'),
          label + ": benchmark body typography")
    check(page.locator(".site-header").evaluate("n => getComputedStyle(n).backgroundColor") == rgb(expected["surface"]),
          label + ": neutral surface header")
    check(page.locator("img").evaluate_all("(nodes) => nodes.every(n => getComputedStyle(n).filter === 'none' && getComputedStyle(n).opacity === '1')"),
          label + ": evidence images are not recolored")
    check(page.evaluate("document.documentElement.scrollWidth <= innerWidth"), label + ": theme has no horizontal overflow")


try:
    validate_files(e)
    verify_followup()
    check(c["example"] == primary_content(walkthrough), "Primary metrics are derived from actual reviewed matched-run provenance")
    check(target_status["achieved"] is expected_target, "Combined target requires >=4/5, valid MAIN, five complete sources, accepted C4 and a last-quarter citation")
    check(target_status["scope"] == "ONE_MATCHED_RUN_ONLY" and target_status["summary"] in (SITE / MARKDOWN).read_text(encoding="utf-8"),
          "Full Markdown carries the same bounded one-run target statement")
    check(extract_markdown((SITE / MARKDOWN).read_bytes().decode("utf-8")) ==
          {row["file"]: (SITE / WALKTHROUGH_PREFIX / row["file"]).read_bytes() for row in walkthrough_rows},
          "Full Markdown roundtrips every authoritative report byte, including footer, JSON, BOM and line endings")
    check(True, "All fourteen approved published files verified; four complete TXT pins and eight image inputs unchanged")
    check((SITE / "examples/real-canvas/real-canvas-coverage.txt").stat().st_size == 58939, "Full 58,939-byte coverage retained")
    check(c["downloads"]["installerIncluded"] and c.get("wordOutput") == word_summary(word),
          "Word-enabled distribution and public example match the complete reviewed release")
    reference = json.loads((SITE / "reference/topic-tool-source.json").read_text(encoding="utf-8"))
    reference_text = json.dumps(reference)
    check(all(value in reference_text for value in
              ("CreateCurrentReviewWord", "FormatCurrentReviewPresentation", "PSR_PRESENTATION_READER_V4_3")),
          "Downloadable topic/tool reference includes the actual Word-enabled sources")
    check(c["hosting"]["liveHttpVerified"] and c["hosting"]["repositoryApiVerified"] and c["hosting"]["pagesConfigured"], "Verified existing public hosting replaces stale planned-state flags")
    escaped = render_text('<script>untrusted()</script>\nA & B <tag>\n', "main")
    check("<script>" not in escaped and "&lt;script&gt;" in escaped, "Report source is escaped, not executable markup")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(str(storage / "browser"), headless=True, accept_downloads=True)
        def route(request_route):
            if urlparse(request_route.request.url).hostname != "127.0.0.1":
                result["externalRequests"].append("Blocked external request")
                request_route.abort()
            else:
                request_route.continue_()
        context.route("**/*", route)
        page = context.pages[0]
        page.on("pageerror", lambda error: result["errors"].append("Browser script error"))
        for width, height, theme in [(1440, 1000, "light"), (1440, 1000, "dark"), (390, 844, "light"), (390, 844, "dark"), (320, 800, "light")]:
            label = f"{width}-{theme}"
            page.set_viewport_size({"width": width, "height": height})
            page.goto(args.base_url + "?scoutTheme=" + theme, wait_until="networkidle")
            check_theme(page, theme, label + ": homepage")
            check(page.locator("html").get_attribute("data-theme") == theme, label + ": homepage theme")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": homepage no overflow")
            check(page.locator("main > section").evaluate_all("(nodes)=>nodes.slice(0,3).map(n=>n.id).join(',')") == "word-output,showcase,full-example", label + ": Word release leads; unchanged real journey still precedes its complete report")
            check(page.locator("figure.screenshot img").count() == 9, label + ": exact nine matched native derivatives")
            check(page.locator("figure.screenshot").evaluate_all("(nodes)=>nodes.map(n=>n.dataset.imageRole)") == list(IMAGE_ROLES), label + ": all matched image roles in the agreed presentation order")
            check(page.locator(".journey-number").all_text_contents() == ["01", "02", "03", "04", "05", "06"], label + ": upload, trigger, agent, results, email and open report are six ordered stages")
            trigger = page.locator(".journey-stage").nth(1)
            check(trigger.locator("#automatic-intake").count() == 1 and trigger.locator('img[src$="native-flow-run.png"]').count() == 1, label + ": step two uses the actual matched flow run")
            check(all(text in trigger.text_content() for text in ["When a file is created (properties only)", "every minute", "A new file, not a new folder", "No chat prompt is needed"]), label + ": automatic handoff and file/folder boundary are explicit")
            check("ExecuteCopilotAsyncV2" in page.locator(".journey-stage").nth(2).text_content(), label + ": step three explains the actual agent invocation")
            check(page.locator(".journey-stage").nth(2).locator('img[src$="native-agent-handoff.png"]').count() == 1, label + ": actual agent-action evidence replaces the historical configuration explainer")
            check(page.locator(".journey-stage").nth(3).locator('img[src$="native-main-opening.png"]').count() == 1 and page.locator(".journey-stage").nth(4).locator('img[src$="native-email-received.png"]').count() == 1, label + ": matched output and received email follow the actual agent action")
            opened_report = page.locator(".journey-stage").nth(5)
            check(opened_report.locator("h2").text_content() == "Open the full report" and opened_report.locator("img").count() == 2 and opened_report.locator('a[href="walkthrough.html"]').count() == 1, label + ": step six uses the matched native assessment/verification views and full reader")
            check(page.locator(".case-metrics strong").all_text_contents() == [f'{walkthrough["accepted"]} / 5', "326 / 326", str(walkthrough["logicalAgentInvocations"])], label + ": actual improved acceptance, complete-input and invocation metrics")
            check(page.locator("#combined-target").text_content() == target_status["summary"]
                  and page.locator("#combined-target").get_attribute("data-combined-target-met") == str(expected_target).lower(),
                  label + ": primary combined-target claim is conditional and one-run only")
            check("GPT-5 Reasoning is not required" in page.locator("#model-choice").text_content() and "GPT5Chat" in page.locator("#reference .config-strip").text_content(), label + ": current GPT5Chat is not confused with historical Reasoning")
            primary_text = page.locator("#showcase, #full-example").all_text_contents()
            check(not re.search(r"(?<!\d)1\s*/\s*5|80\s*/\s*326|not verified Inbox receipt", " ".join(primary_text)), label + ": no historical outcome, prefix coverage or unverified-receipt caveat in primary evidence")
            check("historical" in page.locator("#history").text_content().lower() and page.locator('#history a[href="full-example.html"]').count() == 1, label + ": immutable historical example remains explicitly separate")
            improvement = page.locator("#coverage-improvements")
            check(all(text.lower() in improvement.text_content().lower() for text in ["not an app pass rate", "at least 4/5", "at least 90%", "not achieved together in these two historical no-email benchmark runs", "failed and unsupported sources stay visible", "deterministic MAIN", "0/5"]), label + ": benchmark target limitations are explicitly historical, with regressions retained")
            check(page.locator(".follow-up-metrics strong").all_text_contents() == ["3 / 5", "326 / 326", "2 / 2"], label + ": exact repeat-run acceptance, supplied screen and MAIN metrics")
            check(page.locator('.showcase-review-note a[href="#coverage-improvements"]').count() == 1, label + ": the observed partial result links directly to its improvement plan")
            check("Owner Inbox receipt and the matching protected-report link verified" in page.locator("#example-caveat").text_content(), label + ": actual receipt and protected-report proof beside primary example")
            check("Forwarded corporate receipt is not established" in page.locator("#delivery-boundary").text_content(), label + ": owner receipt does not imply corporate forwarding receipt")
            check("no-email" in improvement.text_content() and improvement.locator("tbody tr").count() == 11, label + ": both no-email benchmarks and all 11 historical comparisons remain distinct")
            expected_zips = {e["bundle"]["path"]}
            if solutions:
                expected_zips.update(row["path"] for row in solutions["files"].values()
                                     if row["path"].endswith(".zip"))
            else:
                expected_zips.add(WORD_PATHS["bundle"])
            check(set(page.locator('a[href$=".zip"]').evaluate_all("(nodes)=>nodes.map(n=>n.getAttribute('href'))"))
                  == expected_zips,
                  label + ": only the exact evidence and declared solution/resource ZIPs")
            box = page.locator('nav a[href="#solution-download"]').bounding_box()
            check(box["y"] + box["height"] < height, label + ": Word solution download navigation above fold")
            check(page.locator("#word-output h1").bounding_box()["y"] < height - 24,
                  label + ": Word-output headline begins in the initial viewport")
            page.evaluate("async()=>{for(const i of document.images){i.loading='eager';await i.decode();}}")
            page.evaluate("scrollTo(0,0)")
            if width != 320:
                capture(page, "home-" + label + ".png")
            page.goto(urljoin(args.base_url, "walkthrough.html?scoutTheme=" + theme), wait_until="networkidle")
            check_theme(page, theme, label + ": matched reader")
            check(page.locator("html").get_attribute("data-theme") == theme, label + ": matched reader theme")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": matched reader no overflow")
            check(page.locator("#main .report-text h3").count() == 10, label + ": matched reader retains all ten MAIN headings")
            check(page.locator("#combined-target").text_content() == target_status["summary"]
                  and page.locator("#combined-target").get_attribute("data-combined-target-met") == str(expected_target).lower(),
                  label + ": matched reader agrees with conditional homepage/Markdown target metadata")
            check(page.locator(".report-text pre").evaluate_all("(nodes)=>nodes.every(n=>getComputedStyle(n).maxHeight==='none'&&getComputedStyle(n).overflowY==='visible')"), label + ": matched reports have no clipping or height limits")
            for row in walkthrough_rows:
                check(page.locator('[data-walkthrough-text="' + row["file"] + '"]').text_content() == normalized_text((SITE / WALKTHROUGH_PREFIX / row["file"]).read_bytes()), label + ": complete matched DOM/source equality — " + row["file"])
            check(page.locator(".report-text a, .report-text script, .report-text img").count() == 0, label + ": matched source text is escaped and cannot create live links or markup")
            if width != 320:
                capture(page, "walkthrough-" + label + ".png")
            page.goto(urljoin(args.base_url, "full-example.html?scoutTheme=" + theme), wait_until="networkidle")
            check_theme(page, theme, label + ": historical reader")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": reader no overflow")
            check(page.locator("#main .report-text h3").count() == 10, label + ": all MAIN headings")
            check(page.locator(".report-text pre").evaluate_all("(nodes)=>nodes.every(n=>getComputedStyle(n).maxHeight==='none'&&getComputedStyle(n).overflowY==='visible')"), label + ": no clipped or height-limited report")
            for name, kind, _ in DOCUMENTS:
                check(page.locator('[data-example-text="' + kind + '"]').text_content() == (SITE / "examples/real-canvas" / name).read_bytes().decode("utf-8-sig"), label + ": complete exact text — " + kind)
            check(page.locator(".report-text a").count() == 0, label + ": redaction labels/source strings are not live links")
            if width != 320:
                capture(page, "reader-" + label + ".png")
            page.goto(urljoin(args.base_url, "follow-up.html?scoutTheme=" + theme), wait_until="networkidle")
            check_theme(page, theme, label + ": benchmark reader")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": follow-up reader no overflow")
            check(page.locator("#main .report-text h3").count() == 10, label + ": follow-up has all ten MAIN headings")
            check(page.locator("[data-followup-text]").text_content() == (SITE / "examples/follow-up/complete-review.txt").read_text(encoding="utf-8"), label + ": complete follow-up text retained with HTML newline normalization only")
            check("4/5 combined target remained unmet in these two historical no-email benchmark runs" in page.locator(".example-lead").text_content(), label + ": benchmark reader scopes its unmet target to those historical runs")
            if width != 320:
                capture(page, "followup-" + label + ".png")

        for name in ("index.html", "walkthrough.html", "full-example.html", "follow-up.html"):
            for system_theme in ("light", "dark"):
                page.emulate_media(color_scheme=system_theme)
                page.goto(urljoin(args.base_url, name), wait_until="networkidle")
                check_theme(page, "dark", name + ": dark default with " + system_theme + " system")
                opposite = "dark" if system_theme == "light" else "light"
                page.goto(urljoin(args.base_url, name + "?scoutTheme=" + opposite), wait_until="networkidle")
                check_theme(page, opposite, name + ": URL overrides " + system_theme + " system")
                page.locator("#theme-toggle").focus()
                check(page.locator("#theme-toggle").evaluate("n => getComputedStyle(n).outlineWidth") == "3px",
                      name + ": visible keyboard theme focus")
                page.keyboard.press("Enter")
                check_theme(page, system_theme, name + ": keyboard toggle from " + opposite)
                check(page.locator("#theme-toggle").get_attribute("aria-label") == "Switch to " + opposite + " theme",
                      name + ": toggle accessible label follows selected theme")
            page.emulate_media(forced_colors="active")
            check(page.locator("h1").evaluate("n => getComputedStyle(n).backgroundImage === 'none' && getComputedStyle(n).color !== 'rgba(0, 0, 0, 0)'"),
                  name + ": readable solid hero in forced colors")
            page.emulate_media(forced_colors="none", color_scheme="light")

        page.goto(args.base_url, wait_until="networkidle")
        page.keyboard.press("Tab")
        check(page.evaluate("document.activeElement.classList.contains('skip-link')"), "Keyboard skip link first")
        page.keyboard.press("Enter")
        check(page.evaluate("location.hash") == "#main", "Keyboard skip navigation")
        for index in range(len(WALKTHROUGH_IMAGES)):
            link = page.locator("figure.screenshot a.image-link").nth(index)
            href = link.get_attribute("href")
            link.focus()
            page.keyboard.press("Enter")
            check(page.locator("#image-viewer").is_visible(), "Keyboard real-image viewer " + str(index + 1))
            page.locator("#viewer-canvas img").evaluate("image=>image.decode()")
            page.locator("#viewer-zoom").focus()
            page.keyboard.press("Enter")
            check(page.locator("#viewer-zoom").get_attribute("aria-pressed") == "true" and page.locator("#viewer-canvas img").evaluate("i=>getComputedStyle(i).maxWidth") == "none", "Uncropped actual-size inspection " + str(index + 1))
            page.keyboard.press("Escape")
            check(page.evaluate("document.activeElement.getAttribute('href')") == href, "Viewer returns keyboard focus " + str(index + 1))
        page.locator("#instructions-details summary").focus()
        page.keyboard.press("Enter")
        check(page.locator("#instructions-source").text_content()
              == (SITE / "reference/agent-instructions.txt").read_bytes().decode("utf-8"),
              "Complete current Word-enabled project instruction reference retained")
        check(all(word in page.locator("#reference").text_content() for word in ["CollectReviewEvidence", "TaskDialog", "Invoker", "InvokeFlowTaskAction"]), "Actual tool and connection configuration retained")
        check("Native Word output" in page.locator("#report-formats").text_content()
              and "Automated PDF output" in page.locator("#report-formats").text_content(),
              "Implemented Word output is distinct from unimplemented automated PDF")
        check(page.locator("#word-output").count() == 1 and page.locator("#solution-download").count() == 1,
              "Word output and real solution download are prominent")
        check(all(value in page.locator("#word-proof-boundary").text_content()
                  for value in ("synthetic", "site owner", "not", "cross-tenant")),
              "Word proof preserves fixture, recipient and installation limitations")
        check(page.locator("#word-output .word-page").count() == 2,
              "Both public Word pages are visible without pretending they are native captures")
        for role, row in word["files"].items():
            response = context.request.get(urljoin(args.base_url, row["path"]))
            check(response.status == 200 and hashlib.sha256(response.body()).hexdigest() == row["sha256"],
                  "Actual Word-release download matches its reviewed hash: " + role)
        if solutions:
            for role, row in solutions["files"].items():
                response = context.request.get(urljoin(args.base_url, row["path"]))
                check(response.status == 200 and hashlib.sha256(response.body()).hexdigest() == row["sha256"],
                      "Actual import-first download matches its exact hash: " + role)
            for role in ("reviewer", "automation"):
                check(page.locator('#solution-download a.button.primary[href="' + SOLUTION_PATHS[role] + '"]').count() == 1,
                      "Direct unmanaged solution is a primary download: " + role)
            check("Import first." in page.locator("#setup-title").text_content()
                  and "*.target.zip" not in page.locator("#setup").text_content(),
                  "Setup order is import-first, not pre-import substitution")
        page.locator("#theme-toggle").focus()
        current = page.locator("html").get_attribute("data-theme")
        page.keyboard.press("Enter")
        check(page.locator("html").get_attribute("data-theme") != current, "Keyboard theme switch")
        page.locator("[data-full-example-link]").focus()
        page.keyboard.press("Enter")
        page.wait_for_url("**/walkthrough.html")
        for row in walkthrough_rows:
            page.locator('.document-header a[href="' + WALKTHROUGH_PREFIX + "/" + row["file"] + '"]').focus()
            with page.expect_download() as event:
                page.keyboard.press("Enter")
            target = storage / ("matched-" + row["file"])
            event.value.save_as(str(target))
            check(hashlib.sha256(target.read_bytes()).hexdigest() == row["sha256"], "Complete matched keyboard download — " + row["file"])
        page.locator('.reader-actions a[href="' + MARKDOWN + '"]').focus()
        with page.expect_download() as event:
            page.keyboard.press("Enter")
        target = storage / "matched-full-report.md"
        event.value.save_as(str(target))
        check(target.read_bytes() == (SITE / MARKDOWN).read_bytes(), "Browser receives exact complete Markdown derivative")
        check(extract_markdown(target.read_bytes().decode("utf-8")) == {row["file"]: (SITE / WALKTHROUGH_PREFIX / row["file"]).read_bytes() for row in walkthrough_rows}, "Downloaded Markdown is lossless for every authoritative document")
        for link in set(page.locator('a[href^="#"]').evaluate_all("(nodes)=>nodes.map(n=>n.getAttribute('href'))")):
            check(page.locator(link).count() == 1, "Matched reader anchor " + link)
        page.goto(urljoin(args.base_url, "full-example.html"), wait_until="networkidle")
        for name, kind, _ in DOCUMENTS:
            link = page.locator('.document-header a[href="examples/real-canvas/' + name + '"]')
            link.focus()
            with page.expect_download() as event:
                page.keyboard.press("Enter")
            target = storage / name
            event.value.save_as(str(target))
            expected = next(row for row in e["files"] if row["archivePath"] == name)
            check(hashlib.sha256(target.read_bytes()).hexdigest() == expected["sha256"], "Complete keyboard download — " + kind)
        response = context.request.get(urljoin(args.base_url, e["bundle"]["path"]))
        check(response.status == 200 and hashlib.sha256(response.body()).hexdigest() == e["bundle"]["sha256"], "Actual received archive matches displayed manifest")
        with ZipFile(io.BytesIO(response.body())) as z:
            check(len(z.namelist()) == 14 and set(z.namelist()) == {row["archivePath"] for row in e["files"]}, "Exact fourteen-member report/image/provenance archive")
            check(all(z.read(row["archivePath"]) == (SITE / row["path"]).read_bytes() for row in e["files"]), "Every archive member is complete and exactly pinned")
            check(len(z.read("real-canvas-coverage.txt")) == 58939, "Downloaded bundle includes all coverage bytes")
        for name in DEPLOY:
            check(context.request.get(urljoin(args.base_url, name)).status == 200, "Declared current local resource: " + name)
        for target in ["_private-hold/", ".qa-work/", "tools/qa_site.py", "../README.md"]:
            check(context.request.get(urljoin(args.base_url, target)).status == 404, "Nonpublic/holding path blocked")
        for link in set(page.locator('a[href^="#"]').evaluate_all("(nodes)=>nodes.map(n=>n.getAttribute('href'))")):
            check(page.locator(link).count() == 1, "Complete reader anchor " + link)
        page.set_viewport_size({"width": 1440, "height": 1200})
        page.goto(urljoin(args.base_url, "full-example.html?scoutTheme=light#main-section-1"), wait_until="networkidle")
        page.emulate_media(reduced_motion="reduce")
        page.locator("#main-section-1").evaluate("node=>scrollTo(0,node.getBoundingClientRect().top+scrollY-48)")
        capture(page, "main-reading.png")
        page.goto(urljoin(args.base_url, "full-example.html?scoutTheme=dark"), wait_until="networkidle")
        page.evaluate("window.print=()=>{window.__printRequested=true}")
        page.locator("#print-example").focus()
        page.keyboard.press("Enter")
        check(page.evaluate("window.__printRequested===true"), "Print button invokes browser print (intercepted wiring test)")
        page.emulate_media(media="print")
        check(page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--cp-text').trim()") == "#242424", "Light print palette from dark reader")
        pdf_bytes = page.pdf(format="A4", print_background=False, prefer_css_page_size=True, display_header_footer=False)
        (captures / "local-complete-print.pdf").write_bytes(pdf_bytes)
        pdf = PdfReader(io.BytesIO(pdf_bytes))
        printed = compact("\n".join(sheet.extract_text() or "" for sheet in pdf.pages))
        for name, kind, _ in DOCUMENTS:
            check(compact((SITE / "examples/real-canvas" / name).read_bytes().decode("utf-8-sig")) in printed, "Actual browser PDF contains complete text — " + kind)
        result["printValidation"] = {"allSixHistoricalDocumentsComplete": True, "historicalPages": len(pdf.pages), "publicPdfIncluded": False, "runtimeFormatterExecuted": False}
        page.set_viewport_size({"width": 794, "height": 1123})
        capture(page, "print-layout.png")
        plain_context = context.browser.new_context(java_script_enabled=False)
        plain_context.route("**/*", route)
        plain = plain_context.new_page()
        plain.goto(args.base_url, wait_until="networkidle")
        check(plain.locator("#example-caveat").text_content() == primary_content(walkthrough)["briefCaveat"], "No-JavaScript homepage retains exact improved metrics and receipt proof")
        check(plain.locator("#combined-target").text_content() == combined_target(walkthrough)["summary"], "No-JavaScript homepage retains bounded target evidence")
        check(plain.locator("figure.screenshot a.image-link").count() == 9 and plain.locator('[data-full-example-link]').get_attribute("href") == "walkthrough.html", "No-JavaScript image inspection and main reader links")
        expected_downloads = ({SOLUTION_PATHS[role] for role in ("reviewer", "automation", "support")}
                              if solutions else {WORD_PATHS["bundle"]})
        check(set(plain.locator('#solution-download a[download]').evaluate_all(
                  "(nodes)=>nodes.map(n=>n.getAttribute('href'))")) == expected_downloads
              and plain.locator('#word-output a[href="' + WORD_PATHS["example"] + '"]').count() == 1,
              "Word example and exact declared solution/resource downloads are accessible without JavaScript")
        check(plain.locator("#instructions-source").text_content() == (SITE / "reference/agent-instructions.txt").read_text(encoding="utf-8")
              and json.loads(plain.locator("#topics-source").text_content()) == reference,
              "No-JavaScript source blocks match the complete current reference downloads")
        plain.goto(urljoin(args.base_url, "walkthrough.html"), wait_until="networkidle")
        check(plain.locator("#combined-target").text_content() == combined_target(walkthrough)["summary"], "No-JavaScript reader retains the same bounded target evidence")
        for row in walkthrough_rows:
            check(plain.locator('[data-walkthrough-text="' + row["file"] + '"]').text_content() == normalized_text((SITE / WALKTHROUGH_PREFIX / row["file"]).read_bytes()), "Complete matched report without JavaScript — " + row["file"])
        page.emulate_media(media="screen")
        page.goto(urljoin(args.base_url, "walkthrough.html?scoutTheme=dark"), wait_until="networkidle")
        page.evaluate("window.print=()=>{window.__printRequested=true}")
        page.locator("#print-example").focus()
        page.keyboard.press("Enter")
        check(page.evaluate("window.__printRequested===true"), "Matched reader keyboard print wiring")
        page.emulate_media(media="print")
        check(page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--cp-text').trim()") == "#242424", "Matched reader light print palette from dark theme")
        matched_pdf = page.pdf(format="A4", print_background=False, prefer_css_page_size=True, display_header_footer=False)
        (captures / "local-walkthrough-print.pdf").write_bytes(matched_pdf)
        matched_pages = PdfReader(io.BytesIO(matched_pdf)).pages
        matched_printed = compact("\n".join(sheet.extract_text() or "" for sheet in matched_pages))
        for row in walkthrough_rows:
            check(compact(normalized_text((SITE / WALKTHROUGH_PREFIX / row["file"]).read_bytes()).lstrip("\ufeff")) in matched_printed, "Actual browser PDF retains full matched content — " + row["file"])
        result["printValidation"].update(allMatchedDocumentsComplete=True, matchedPages=len(matched_pages))
        plain.goto(urljoin(args.base_url, "full-example.html"), wait_until="networkidle")
        for name, kind, _ in DOCUMENTS:
            check(plain.locator('[data-example-text="' + kind + '"]').text_content() == (SITE / "examples/real-canvas" / name).read_bytes().decode("utf-8-sig"), "Complete without JavaScript — " + kind)
        plain.goto(urljoin(args.base_url, "follow-up.html"), wait_until="networkidle")
        check(plain.locator("[data-followup-text]").text_content() == (SITE / "examples/follow-up/complete-review.txt").read_text(encoding="utf-8"), "Complete new MAIN is readable without JavaScript")
        page.goto(urljoin(args.base_url, "follow-up.html?scoutTheme=dark"), wait_until="networkidle")
        page.emulate_media(media="print")
        followup_pdf = page.pdf(format="A4", print_background=False, prefer_css_page_size=True, display_header_footer=False)
        (captures / "local-followup-print.pdf").write_bytes(followup_pdf)
        followup_printed = compact("\n".join(sheet.extract_text() or "" for sheet in PdfReader(io.BytesIO(followup_pdf)).pages))
        check(compact((SITE / "examples/follow-up/complete-review.txt").read_text(encoding="utf-8")) in followup_printed, "Actual browser PDF contains the complete follow-up MAIN and footer")
        plain_context.close()
        check(not result["externalRequests"], "No external browser requests")
        check(not result["errors"], "No browser script errors")
        context.close()
    for prefix in ["home", "reader", "walkthrough"]:
        first = Image.open(captures / (prefix + "-1440-light.png")).convert("RGB")
        board = Image.new("RGB", (1500, 1000), first.getpixel((0, first.height - 1)))
        for suffix, xy, size in [("1440-light", (0, 0), (720, 500)), ("1440-dark", (0, 500), (720, 500)), ("390-light", (720, 0), (390, 844)), ("390-dark", (1110, 0), (390, 844))]:
            image = Image.open(captures / (prefix + "-" + suffix + ".png")).convert("RGB")
            board.paste(image.resize(size, Image.Resampling.LANCZOS), xy)
        board.save(captures / (prefix + "-contact.png"))
    result["status"] = "PASS"
finally:
    if (storage / "owned-by-real-qa").is_file():
        shutil.rmtree(storage)
    (SITE / "qa/RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"Fresh real-example QA {result['status']}: {len(result['cases'])} checks; no previous QA inherited.")
