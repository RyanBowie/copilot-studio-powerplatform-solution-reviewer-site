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
from public_inventory import IMAGES, DEPLOY
from prepare_real_example import validate_files, DOCUMENTS, TEXT_PINS, render_text

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--base-url", default="http://127.0.0.1:4178/preview/")
parser.add_argument("--capture-directory", type=Path, required=True)
args = parser.parse_args()
captures = args.capture_directory.resolve()
if urlparse(args.base_url).hostname != "127.0.0.1" or not captures.is_relative_to(SITE):
    raise SystemExit("Only a local preview and owned private capture directory are allowed.")
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
result = {"status": "PENDING", "scope": "APPROVED_REAL_CANVAS_LOCAL_SITE_QA",
          "historicalQaInherited": False, "runtimeActionsPerformed": False, "capturesPublished": False,
          "contentSourceSha256": hashlib.sha256((SITE / "content.json").read_bytes()).hexdigest(),
          "exampleBundleSha256": e["bundle"]["sha256"], "cases": [], "externalRequests": [], "errors": []}


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


try:
    validate_files(e)
    check(True, "All fourteen approved published files verified; four complete TXT pins and eight image inputs unchanged")
    check((SITE / "examples/real-canvas/real-canvas-coverage.txt").stat().st_size == 58939, "Full 58,939-byte coverage retained")
    check(not c["downloads"]["installerIncluded"], "Installer remains excluded")
    check(not c["hosting"]["liveHttpVerified"] and not c["hosting"]["repositoryApiVerified"], "Clean replacement hosting is not falsely reported as created/live")
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
            check(page.locator("html").get_attribute("data-theme") == theme, label + ": homepage theme")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": homepage no overflow")
            check(page.locator("main > section").evaluate_all("(nodes)=>nodes.slice(0,2).map(n=>n.id).join(',')") == "showcase,full-example", label + ": actual journey followed immediately by complete-output entry")
            check(page.locator("figure.screenshot img").count() == 8, label + ": exact eight current real-review derivatives")
            check(page.locator(".journey-number").all_text_contents() == ["01", "02", "03", "04", "05", "06"], label + ": upload, trigger, agent, results, email and open report are six ordered stages")
            trigger = page.locator(".journey-stage").nth(1)
            check(trigger.locator("#automatic-intake").count() == 1 and trigger.locator("img").count() == 0, label + ": step two explains the trigger instead of showing a report or fabricated run capture")
            check(all(text in trigger.text_content() for text in ["When a file is created (properties only)", "every minute", "not a run-history screenshot", "A new file, not a new folder", "No chat prompt is needed"]), label + ": automatic handoff and file/folder boundary are explicit")
            check("ExecuteCopilotAsyncV2" in page.locator(".journey-stage").nth(2).text_content(), label + ": step three explains the actual agent invocation")
            check(page.locator(".journey-stage").nth(3).locator('img[src$="actual-result-review-txt.png"]').count() == 1 and page.locator(".journey-stage").nth(4).locator('img[src$="user-provided-notification-body.png"]').count() == 1, label + ": actual saved report and notification follow the agent")
            opened_report = page.locator(".journey-stage").nth(5)
            check(opened_report.locator("h2").text_content() == "Open the full report" and opened_report.locator("img").count() == 3 and opened_report.locator('a[href="full-example.html"]').count() == 1, label + ": step six uses all three user report screenshots and links the complete report")
            check(page.locator(".case-metrics strong").all_text_contents() == ["1 / 5", "80 / 326", "6"], label + ": actual Partial/coverage/call metrics")
            check("not verified Inbox receipt" in page.locator("#example-caveat").text_content(), label + ": receipt caveat beside example")
            check(page.locator('img[src$="user-provided-notification-body.png"]').count() == 1, label + ": requested user-provided notification is the lead notification image")
            check(set(page.locator('a[href$=".zip"]').evaluate_all("(nodes)=>nodes.map(n=>n.getAttribute('href'))")) == {e["bundle"]["path"]}, label + ": only the approved real-example ZIP")
            box = page.locator("[data-full-example-link]").bounding_box()
            check(box["y"] + box["height"] < height, label + ": full output link above fold")
            check(page.locator(".screenshot-journey img").first.bounding_box()["y"] < height - 24, label + ": first actual capture begins in initial viewport")
            page.evaluate("async()=>{for(const i of document.images){i.loading='eager';await i.decode();}}")
            page.evaluate("scrollTo(0,0)")
            if width != 320:
                capture(page, "home-" + label + ".png")
            page.goto(urljoin(args.base_url, "full-example.html?scoutTheme=" + theme), wait_until="networkidle")
            check(page.evaluate("document.documentElement.scrollWidth<=innerWidth"), label + ": reader no overflow")
            check(page.locator("#main .report-text h3").count() == 10, label + ": all MAIN headings")
            check(page.locator(".report-text pre").evaluate_all("(nodes)=>nodes.every(n=>getComputedStyle(n).maxHeight==='none'&&getComputedStyle(n).overflowY==='visible')"), label + ": no clipped or height-limited report")
            for name, kind, _ in DOCUMENTS:
                check(page.locator('[data-example-text="' + kind + '"]').text_content() == (SITE / "examples/real-canvas" / name).read_bytes().decode("utf-8-sig"), label + ": complete exact text — " + kind)
            check(page.locator(".report-text a").count() == 0, label + ": redaction labels/source strings are not live links")
            if width != 320:
                capture(page, "reader-" + label + ".png")

        page.goto(args.base_url, wait_until="networkidle")
        page.keyboard.press("Tab")
        check(page.evaluate("document.activeElement.classList.contains('skip-link')"), "Keyboard skip link first")
        page.keyboard.press("Enter")
        check(page.evaluate("location.hash") == "#main", "Keyboard skip navigation")
        for index in range(8):
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
        check(page.locator("#instructions-source").text_content().startswith("Power Platform Solution Reviewer"), "Complete project instruction reference retained")
        check(all(word in page.locator("#reference").text_content() for word in ["CollectReviewEvidence", "TaskDialog", "Invoker", "InvokeFlowTaskAction"]), "Actual tool and connection configuration retained")
        check("not implemented" in page.locator("#report-formats").text_content(), "Optional document formatter not passed off as implemented")
        page.locator("#theme-toggle").focus()
        current = page.locator("html").get_attribute("data-theme")
        page.keyboard.press("Enter")
        check(page.locator("html").get_attribute("data-theme") != current, "Keyboard theme switch")
        page.locator("[data-full-example-link]").focus()
        page.keyboard.press("Enter")
        page.wait_for_url("**/full-example.html")
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
        result["printValidation"] = {"allSixDocumentsComplete": True, "pages": len(pdf.pages), "publicPdfIncluded": False, "runtimeFormatterExecuted": False}
        page.set_viewport_size({"width": 794, "height": 1123})
        capture(page, "print-layout.png")
        plain_context = context.browser.new_context(java_script_enabled=False)
        plain_context.route("**/*", route)
        plain = plain_context.new_page()
        plain.goto(urljoin(args.base_url, "full-example.html"), wait_until="networkidle")
        for name, kind, _ in DOCUMENTS:
            check(plain.locator('[data-example-text="' + kind + '"]').text_content() == (SITE / "examples/real-canvas" / name).read_bytes().decode("utf-8-sig"), "Complete without JavaScript — " + kind)
        plain_context.close()
        check(not result["externalRequests"], "No external browser requests")
        check(not result["errors"], "No browser script errors")
        context.close()
    for prefix in ["home", "reader"]:
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
