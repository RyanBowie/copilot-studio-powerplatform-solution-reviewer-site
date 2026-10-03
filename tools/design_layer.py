"""Shared design-layer snippets for the public documentation pages."""
from pathlib import Path
import html

SITE_NAME = "Power Platform Solution Reviewer"
BASE_URL = "https://ryanbowie.github.io/copilot-studio-powerplatform-solution-reviewer-site/"

ENTITY_MAP = str.maketrans({
    chr(0x00B7): "&middot;", chr(0x2013): "&ndash;", chr(0x2014): "&mdash;", chr(0x2019): "&rsquo;",
    chr(0x201C): "&ldquo;", chr(0x201D): "&rdquo;", chr(0x2191): "&uarr;", chr(0x2192): "&rarr;",
    chr(0x2193): "&darr;", chr(0x2260): "&ne;", chr(0x2264): "&le;", chr(0x2265): "&ge;",
})

def html_entities(value):
    return value.translate(ENTITY_MAP)

PALETTE_STYLE = """
:root {
  color-scheme: light;
  --cp-bg: #f2f2f8;
  --cp-bg-elevated: #f8f7fc;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f2f2f8;
  --cp-border: #e3dfed;
  --cp-border-strong: #9285aa;
  --cp-text: #102631;
  --cp-text-muted: #52637a;
  --cp-text-soft: #667287;
  --cp-accent: #7653ae;
  --cp-accent-hover: #58378b;
  --cp-accent-soft: #eee8f7;
  --cp-accent-fg: #ffffff;
  --cp-success: #207346;
  --cp-danger: #b4233e;
  --cp-warning: #8c6208;
  --cp-link: #066bc7;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(118, 83, 174, 0.12);
  --cp-chart-blue: #0877dd;
  --cp-chart-indigo: #5364ba;
  --cp-chart-purple: #7653ae;
  --cp-chart-violet: #9651bb;
  --cp-chart-magenta: #b535c3;
  --cp-chart-track: #e8e3f0;
  --cp-transparent: transparent;
}
html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #171717;
  --cp-bg-elevated: #222222;
  --cp-surface: #1f1f1f;
  --cp-surface-soft: #262626;
  --cp-border: #3b3b3b;
  --cp-border-strong: #858585;
  --cp-text: #f2f2f2;
  --cp-text-muted: #bdbdbd;
  --cp-text-soft: #aaaaaa;
  --cp-accent: #c3a0ef;
  --cp-accent-hover: #debeff;
  --cp-accent-soft: #2b2b2b;
  --cp-accent-fg: #181818;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #80baff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(31, 31, 31, 0.88);
  --cp-panel: rgba(31, 31, 31, 0.72);
  --cp-panel-strong: rgba(31, 31, 31, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(195, 160, 239, 0.12);
  --cp-chart-blue: #69aeff;
  --cp-chart-indigo: #98a5ff;
  --cp-chart-purple: #bc98ed;
  --cp-chart-violet: #d097ee;
  --cp-chart-magenta: #ed8fea;
  --cp-chart-track: #3b3b3b;
  --cp-transparent: transparent;
}
@media print {
  html[data-theme="dark"] {
    color-scheme: light;
    --cp-bg: #f2f2f8;
    --cp-bg-elevated: #f8f7fc;
    --cp-surface: #ffffff;
    --cp-surface-soft: #f2f2f8;
    --cp-border: #e3dfed;
    --cp-border-strong: #9285aa;
    --cp-text: #242424;
    --cp-text-muted: #52637a;
    --cp-text-soft: #667287;
    --cp-accent: #7653ae;
    --cp-accent-hover: #58378b;
    --cp-accent-soft: #eee8f7;
    --cp-accent-fg: #ffffff;
    --cp-success: #207346;
    --cp-danger: #b4233e;
    --cp-warning: #8c6208;
    --cp-link: #066bc7;
    --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
    --cp-overlay: rgba(255, 255, 255, 0.8);
    --cp-panel: rgba(255, 255, 255, 0.86);
    --cp-panel-strong: rgba(255, 255, 255, 0.96);
    --cp-sheen: rgba(255, 255, 255, 0.55);
    --cp-highlight: rgba(118, 83, 174, 0.12);
    --cp-chart-blue: #0877dd;
    --cp-chart-indigo: #5364ba;
    --cp-chart-purple: #7653ae;
    --cp-chart-violet: #9651bb;
    --cp-chart-magenta: #b535c3;
    --cp-chart-track: #e8e3f0;
    --cp-transparent: transparent;
  }
}
"""

DESIGN_CSS = """
/* design-layer:start */
#dl-progress { position: fixed; inset: 0 auto auto 0; z-index: 80; width: 100%; height: 0.25rem; transform-origin: left center; transform: scaleX(0); background: var(--cp-accent); }
html.dl-motion .dl-reveal { opacity: 1; transform: none; transition: opacity .55s ease, transform .55s ease; }
html.dl-motion .dl-reveal.dl-in { opacity: 1; transform: translateY(0); }
.dl-shell { position: relative; overflow: clip; }
.dl-shell::before { content: ""; position: absolute; inset: 0; pointer-events: none; background: radial-gradient(circle at 80% 12%, var(--cp-highlight), var(--cp-transparent) 36%); }
.dl-hero { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(20rem, .95fr); gap: clamp(1.5rem, 4vw, 4rem); align-items: center; padding-block: clamp(3rem, 8vw, 7rem) clamp(2rem, 5vw, 4rem); }
.dl-hero h1 { position: relative; max-width: 12ch; }
@supports (background-clip: text) { .dl-hero h1, .example-intro h1 { background: linear-gradient(105deg, var(--cp-chart-blue), var(--cp-chart-purple) 56%, var(--cp-chart-magenta)); background-clip: text; color: var(--cp-transparent); } }
.dl-hero h1::after { content: ""; display: block; width: min(8rem, 42%); height: .25rem; margin-top: 1rem; border-radius: 999px; background: var(--cp-accent); transform-origin: left center; animation: dl-grow .9s ease-out both; }
@keyframes dl-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
.dl-kicker, .pill { display: inline-flex; align-items: center; gap: .5rem; color: var(--cp-accent); font-size: .76rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
.dl-lede { max-width: 68ch; color: var(--cp-text-muted); font-size: clamp(1.05rem, 2vw, 1.25rem); }
.dl-facts { display: flex; flex-wrap: wrap; gap: .75rem; padding: 0; margin: 1.5rem 0 0; list-style: none; }
.dl-facts li { border: 1px solid var(--cp-border); background: var(--cp-surface); border-radius: 999px; padding: .45rem .8rem; color: var(--cp-text-muted); font-size: .9rem; }
.dl-facts strong { color: var(--cp-text); }
.dl-diagram, .dl-arch { border: 1px solid var(--cp-border); background: var(--cp-panel); border-radius: 1rem; padding: 1rem; box-shadow: var(--cp-shadow); }
.dl-diagram svg, .dl-arch svg { display: block; width: 100%; height: auto; }
.dl-node, .dl-box { fill: var(--cp-surface); stroke: var(--cp-border-strong); stroke-width: 1.5; }
.dl-node-accent { fill: var(--cp-accent-soft); stroke: var(--cp-accent); }
.dl-path { fill: none; stroke: var(--cp-chart-purple); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 8 10; animation: dl-flow 1.6s linear infinite; }
.dl-hot { stroke: var(--cp-chart-blue); stroke-width: 4; }
@keyframes dl-flow { to { stroke-dashoffset: -36; } }
.dl-svg-label { fill: var(--cp-text); font: 700 13px Consolas, "Courier New", Courier, monospace; }
.dl-svg-note { fill: var(--cp-text-muted); font: 11px "Segoe UI", sans-serif; }
.dl-chips { position: sticky; top: 0; z-index: 45; display: flex; gap: .5rem; overflow-x: auto; padding: .65rem max(1rem, calc((100vw - 1280px) / 2)); border-block: 1px solid var(--cp-border); background: var(--cp-panel-strong); }
.dl-chips a { flex: none; padding: .35rem .75rem; border: 1px solid var(--cp-border); border-radius: 999px; background: var(--cp-surface); color: var(--cp-text); text-decoration: none; font-size: .85rem; }
.dl-chips a:hover, .dl-chips a[aria-current="true"] { border-color: var(--cp-accent); color: var(--cp-accent); }
.dl-toc-card { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: 1.5rem; align-items: start; }
.dl-toc-card ol { columns: 2; gap: 2rem; margin: 0; }
.community-notice { border-left-color: var(--cp-accent); }
.downloads-grid { display: grid; gap: 1rem; }
.download-row { display: grid; grid-template-columns: minmax(12rem, 1fr) minmax(12rem, 1.1fr) 7rem 5rem; gap: 1rem; align-items: start; padding: 1rem; border: 1px solid var(--cp-border); border-radius: .75rem; background: var(--cp-surface); }
.download-row strong { display: block; }
.download-row span { display: block; color: var(--cp-text-muted); font-size: .88rem; }
.stepper { counter-reset: step; list-style: none; padding: 0; display: grid; gap: 1rem; }
.stepper li { counter-increment: step; position: relative; padding: 1.25rem 1.25rem 1.25rem 4.25rem; border: 1px solid var(--cp-border); border-radius: .9rem; background: var(--cp-surface); }
.stepper li::before { content: counter(step, decimal-leading-zero); position: absolute; left: 1rem; top: 1rem; display: grid; place-items: center; width: 2.2rem; height: 2.2rem; border-radius: .55rem; background: var(--cp-accent-soft); color: var(--cp-accent); font: 700 .9rem Consolas, "Courier New", Courier, monospace; }
.dl-series { margin-block: 3rem; padding-block: 2rem; border-block: 1px solid var(--cp-border); }
.dl-series-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.dl-series-card { display: flex; flex-direction: column; min-height: 13rem; padding: 1.1rem; border: 1px solid var(--cp-border); border-radius: 1rem; background: var(--cp-surface); text-decoration: none; color: var(--cp-text); }
.dl-series-card[aria-current="page"] { border-color: var(--cp-accent); background: var(--cp-accent-soft); }
.dl-series-card small { color: var(--cp-accent); text-transform: uppercase; letter-spacing: .08em; font-weight: 750; }
.dl-series-card span { margin-top: auto; color: var(--cp-link); font-weight: 650; }
.dl-series-card p { color: var(--cp-text-muted); font-size: .92rem; }
@media (max-width: 900px) { .dl-hero, .dl-toc-card { grid-template-columns: 1fr; } .dl-series-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .download-row { grid-template-columns: 1fr; } }
@media (max-width: 560px) { .dl-series-grid { grid-template-columns: 1fr; } .dl-chips { top: 0; } .dl-hero { padding-block-start: 2rem; } }
@media print { #dl-progress, .dl-chips, .theme-button, .image-viewer { display: none !important; } .dl-reveal { opacity: 1 !important; transform: none !important; } .dl-path { animation: none !important; } h1, .dl-hero h1, .example-intro h1 { background: none !important; color: var(--cp-text) !important; -webkit-text-fill-color: currentColor !important; } }
@media (forced-colors: active) { #dl-progress { forced-color-adjust: none; background: Highlight; } h1, .dl-hero h1 { color: CanvasText !important; -webkit-text-fill-color: CanvasText !important; } }
@media (prefers-reduced-motion: reduce) { .dl-path, .dl-hero h1::after { animation: none !important; } html.dl-motion .dl-reveal { opacity: 1; transform: none; transition: none; } }
/* design-layer:end */
"""

THEME_SCRIPT = """
<script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme = param === "light" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", theme);
  })();
</script>
"""
DESIGN_JS = """
<!-- design-layer-js:start -->
<script>
(() => {
  const start = () => {
  const root = document.documentElement;
  root.classList.add("js");
  const motion = matchMedia("(prefers-reduced-motion: no-preference)").matches;
  if (motion) root.classList.add("dl-motion");
  const progress = document.getElementById("dl-progress");
  const updateProgress = () => {
    if (!progress) return;
    const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    progress.style.transform = "scaleX(" + Math.min(1, scrollY / max).toFixed(4) + ")";
  };
  addEventListener("scroll", updateProgress, { passive: true });
  addEventListener("resize", updateProgress);
  updateProgress();
  if (motion && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add("dl-in"); });
    }, { threshold: 0.08 });
    document.querySelectorAll(".dl-reveal").forEach(node => observer.observe(node));
  } else {
    document.querySelectorAll(".dl-reveal").forEach(node => node.classList.add("dl-in"));
  }
  const anchors = [...document.querySelectorAll(".dl-chips a[href^='#'], .dl-toc-card a[href^='#']")];
  const sections = anchors.map(a => document.getElementById(a.getAttribute("href").slice(1))).filter(Boolean);
  const mark = () => {
    let current = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top < innerHeight * 0.35) current = section;
    anchors.forEach(a => a.setAttribute("aria-current", a.getAttribute("href") === "#" + current.id ? "true" : "false"));
  };
  addEventListener("scroll", mark, { passive: true });
  mark();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
</script>
<!-- design-layer-js:end -->
"""

META_BLOCK = """
<!-- dl-meta:start -->
<meta name="color-scheme" content="dark light">
<link rel="icon" href="data:,">
<meta property="og:title" content="Power Platform Solution Reviewer">
<meta property="og:description" content="A Copilot Studio agent that reviews Power Platform solutions, with a real canvas-app walkthrough, detailed output, Word report output and setup guidance.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ryanbowie.github.io/copilot-studio-powerplatform-solution-reviewer-site/">
<meta property="og:image" content="https://ryanbowie.github.io/copilot-studio-powerplatform-solution-reviewer-site/og.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta property="og:image:alt" content="Power Platform Solution Reviewer documentation with downloads, architecture and setup guidance.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Power Platform Solution Reviewer">
<meta name="twitter:description" content="A Copilot Studio agent that reviews Power Platform solutions, with a real canvas-app walkthrough, detailed output and setup guidance.">
<meta name="twitter:image" content="https://ryanbowie.github.io/copilot-studio-powerplatform-solution-reviewer-site/og.png">
<!-- dl-meta:end -->
"""

SERIES = [
    ("01", "Custom Agent Reporting – Architecture", "https://ryanbowie.github.io/custom-agent-reporting-architecture/", "How a custom Power BI model can report on agents across Copilot Studio, Agent Builder and Microsoft Foundry. Documentation only."),
    ("02", "Copilot Interaction Logging", "https://ryanbowie.github.io/copilot-interaction-logging/", "Build guide: Copilot interaction records from the Purview audit log, collected into Dataverse by two Power Automate flows."),
    ("03", "Power Platform Solution Reviewer", "#top", "A Copilot Studio agent that reviews Power Platform solutions, with a real canvas-app walkthrough, detailed output and setup guidance."),
    ("04", "SharePoint Search Hub", "https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/", "Hub-and-spoke SharePoint search in Copilot Studio, with caller-checked results, a private Excel export and a verified 512-item demo."),
    ("05", "Power BI Agent", "https://ryanbowie.github.io/copilot-studio-powerbi-agent/", "A standard Copilot Studio agent that writes DAX and queries Power BI semantic models as the signed-in user."),
    ("06", "Documentation Builder", "https://ryanbowie.github.io/copilot-studio-documentation-builder/", "Template-aligned Word and PowerPoint documents from Copilot Studio, comparing the Standard and GitHub Copilot harnesses."),
]

def head_extras():
    return META_BLOCK

def style_block():
    return "<style>\n" + PALETTE_STYLE + DESIGN_CSS + "</style>"

def design_js():
    return DESIGN_JS

def signal_diagram():
    return '''<div class="dl-diagram" aria-label="Solution review signal diagram"><svg viewBox="0 0 680 360" role="img" aria-labelledby="signal-title signal-desc"><title id="signal-title">Solution reviewer flow</title><desc id="signal-desc">A solution package enters private storage, is collected by Power Automate, assessed by Copilot Studio and saved as protected report outputs.</desc><path class="dl-path dl-hot" d="M185 110 H265 M415 110 H495"/><path class="dl-path" d="M310 260 H390"/><rect class="dl-node dl-node-accent" x="35" y="70" width="150" height="80" rx="16"/><text class="dl-svg-label" x="110" y="102" text-anchor="middle">Solution ZIP</text><text class="dl-svg-note" x="110" y="125" text-anchor="middle">Incoming storage</text><rect class="dl-node" x="265" y="70" width="150" height="80" rx="16"/><text class="dl-svg-label" x="340" y="102" text-anchor="middle">Power Automate</text><text class="dl-svg-note" x="340" y="125" text-anchor="middle">Collector + gates</text><rect class="dl-node dl-node-accent" x="495" y="70" width="150" height="80" rx="16"/><text class="dl-svg-label" x="570" y="102" text-anchor="middle">Copilot Studio</text><text class="dl-svg-note" x="570" y="125" text-anchor="middle">Grounded review</text><rect class="dl-node" x="150" y="220" width="160" height="80" rx="16"/><text class="dl-svg-label" x="230" y="252" text-anchor="middle">Protected report</text><text class="dl-svg-note" x="230" y="275" text-anchor="middle">TXT / Markdown / Word</text><rect class="dl-node" x="390" y="220" width="160" height="80" rx="16"/><text class="dl-svg-label" x="470" y="252" text-anchor="middle">Requester link</text><text class="dl-svg-note" x="470" y="275" text-anchor="middle">Bounded email proof</text></svg></div>'''

def architecture_diagram():
    return '''<section class="section wrap dl-reveal" id="architecture"><div class="section-heading"><p class="eyebrow">Architecture</p><h2>Import-first solutions.<br>Evidence-first output.</h2><p>The downloadable packages keep collection, assessment and report output separated. Import does not enable intake, publish the agent or prove production readiness.</p></div><div class="dl-arch"><svg viewBox="0 0 900 360" role="img" aria-labelledby="arch-title arch-desc"><title id="arch-title">Power Platform Solution Reviewer architecture</title><desc id="arch-desc">The reviewer solution contains the agent and review helpers. The automation solution handles intake, storage, report generation and notification. Target configuration binds connections and template schema after import.</desc><path class="dl-path dl-hot" d="M240 160 H330"/><path class="dl-path" d="M570 160 H660"/><path class="dl-path" d="M450 215 V270"/><rect class="dl-box dl-node-accent" x="40" y="105" width="200" height="110" rx="18"/><text class="dl-svg-label" x="140" y="145" text-anchor="middle">Reviewer solution</text><text class="dl-svg-note" x="140" y="170" text-anchor="middle">Agent, topics, Word helper</text><rect class="dl-box" x="330" y="105" width="240" height="110" rx="18"/><text class="dl-svg-label" x="450" y="145" text-anchor="middle">Automation solution</text><text class="dl-svg-note" x="450" y="170" text-anchor="middle">Intake, gates, outputs</text><rect class="dl-box dl-node-accent" x="660" y="105" width="200" height="110" rx="18"/><text class="dl-svg-label" x="760" y="145" text-anchor="middle">Target setup</text><text class="dl-svg-note" x="760" y="170" text-anchor="middle">Connections + template</text><rect class="dl-box" x="330" y="270" width="240" height="60" rx="14"/><text class="dl-svg-label" x="450" y="306" text-anchor="middle">Stopped until approved</text></svg></div></section>'''

def community_notice():
    return '''<section class="section wrap community-notice dl-reveal" id="read-this-first"><p class="pill">Community project. This is not a Microsoft product.</p><div class="notice"><p><strong>Read this first.</strong> This community project is shared as-is under the MIT licence. It is not a Microsoft product, is not supported by Microsoft, and has no SLA or warranty.</p><p>Test in a non-production environment first. Get your organisation's approvals before importing any solution into an environment that holds real data, and assess the security, operational and support responsibilities yourself.</p></div></section>'''

def chips(items=None):
    if items is None:
        items = [("top", "Overview"), ("read-this-first", "Read this first"), ("downloads", "Downloads"), ("architecture", "Architecture"), ("showcase", "Walkthrough"), ("setup", "Setup"), ("history", "History")]
    links = "".join(f'<a href="#{html.escape(anchor, quote=True)}">{html.escape(label)}</a>' for anchor, label in items)
    return f'<nav class="dl-chips" aria-label="Page sections">{links}</nav>'

def toc_card():
    return '''<section class="section wrap dl-reveal" id="contents"><div class="card dl-toc-card"><div><p class="eyebrow">Contents</p><h2>What to inspect first.</h2><p>Start with the licence and support boundary, then download only the artefacts you need for a controlled non-production import.</p></div><ol><li><a href="#read-this-first">Community and support notice</a></li><li><a href="#downloads">All downloadable files</a></li><li><a href="#architecture">Architecture and import boundary</a></li><li><a href="#showcase">Real canvas-app walkthrough</a></li><li><a href="#full-example">Complete output evidence</a></li><li><a href="#setup">Step-by-step setup</a></li></ol></div></section>'''

SOLUTION_ONLY_DOWNLOADS = {
    "downloads/psr_PowerPlatformSolutionReviewer_3_3_2_7_unmanaged.zip",
    "downloads/psr_PowerPlatformSolutionAutomation_3_3_2_7_unmanaged.zip",
    "downloads/solution-reviewer-setup-3.3.2.7.zip",
    "downloads/SOLUTION-IMPORT-SETUP.md",
    "downloads/solution-import-release.json",
}
# The configure-before-import bundle is offered only when no direct solutions are released.
BUNDLE_ONLY_DOWNLOADS = {
    "downloads/solution-reviewer-word-output-3.3.2.6.bundle.zip",
    "downloads/WORD-OUTPUT-SETUP.md",
    "downloads/word-output-release.json",
}

def download_rows(site, solutions=True):
    hidden = BUNDLE_ONLY_DOWNLOADS if solutions else SOLUTION_ONLY_DOWNLOADS
    rows = [
        ("Reviewer unmanaged solution", "Import first. Contains the agent and helper components.", "3.3.2.7", "downloads/psr_PowerPlatformSolutionReviewer_3_3_2_7_unmanaged.zip"),
        ("Automation unmanaged solution", "Import second. Contains the automatic review implementation.", "3.3.2.7", "downloads/psr_PowerPlatformSolutionAutomation_3_3_2_7_unmanaged.zip"),
        ("Setup resources", "Supplementary post-import tooling; not a solution import input.", "3.3.2.7", "downloads/solution-reviewer-setup-3.3.2.7.zip"),
        ("Import and setup guide", "Step-by-step configure-after-import instructions.", "3.3.2.7", "downloads/SOLUTION-IMPORT-SETUP.md"),
        ("Import release manifest", "Exact file and member hashes plus native import evidence.", "3.3.2.7", "downloads/solution-import-release.json"),
        ("Historical Word-output bundle", "Configure-before-import historical package retained for reference.", "3.3.2.6", "downloads/solution-reviewer-word-output-3.3.2.6.bundle.zip"),
        ("Historical Word setup guide", "Configure-before-import instructions for the older bundle.", "3.3.2.6", "downloads/WORD-OUTPUT-SETUP.md"),
        ("Word template", "Template used by the Word output flow.", "4.3.1", "downloads/current-review-v4.3.1.web.template.docx"),
        ("Redacted Word example", "Privacy-redacted derivative of the synthetic format-only output.", "4.3.1", "examples/word-output/review-example.docx"),
        ("Word-output release manifest", "Hashes and evidence for the historical Word bundle and example.", "3.3.2.6", "downloads/word-output-release.json"),
        ("Historical evidence bundle", "Four TXT reports, eight images and provenance records.", "historical", "downloads/real-canvas-review-example.zip"),
        ("Historical evidence manifest", "Input and archive hashes for the historical example.", "historical", "downloads/real-canvas-example-manifest.json"),
        ("Matched full Markdown report", "Presentation-only derivative containing every authoritative source file.", "3.3.2.5", "examples/walkthrough-325/complete-review.md"),
        ("Matched MAIN report", "Authoritative complete MAIN TXT.", "3.3.2.5", "examples/walkthrough-325/MAIN.txt"),
        ("Matched component reports", "Accepted C1, C2, C3 and C4 TXT files plus inventory and coverage JSON.", "3.3.2.5", "walkthrough.html"),
    ]
    parts = []
    root = Path(site)
    for title, detail, version, href in rows:
        if href in hidden:
            continue
        size = "page"
        path = root / href
        if path.is_file():
            size = f"{path.stat().st_size:,} bytes"
        download = ' download' if path.suffix.lower() in {'.zip', '.docx', '.md', '.txt'} else ''
        parts.append(f'<div class="download-row"><div><strong><a href="{href}"{download}>{html.escape(title)}</a></strong><span>{html.escape(detail)}</span></div><span>{html.escape(version)}</span><span>{size}</span><span><a href="{href}">Open →</a></span></div>')
    return "".join(parts)

def downloads_section(site, solutions=True):
    return f'''<section class="section wrap dl-reveal" id="downloads"><div class="section-heading"><p class="eyebrow">Downloads</p><h2>Every downloadable artefact.<br>With the import boundary visible.</h2><p>Links point to files in this repository. There are no GitHub Releases for this site.</p></div><div class="downloads-grid">{download_rows(site, solutions)}</div></section>'''

def series_block():
    cards = []
    for number, title, href, desc in SERIES:
        current = ' aria-current="page"' if href == "#top" else ""
        label = "You are here" if href == "#top" else "Open →"
        cards.append(f'<a class="dl-series-card" href="{href}"{current}><small>{number}</small><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p><span>{label}</span></a>')
    return '<!-- dl-series:start --><section class="wrap dl-series" id="more-projects" aria-label="More community projects"><p class="eyebrow">More community projects</p><h2>More community projects</h2><div class="dl-series-grid">' + "".join(cards) + '</div></section><!-- dl-series:end -->'

def footer(extra=''):
    return f'''{series_block()}<footer class="wrap site-footer"><p><strong>{SITE_NAME}</strong> · MIT licence · <a href="README.md">README</a> · <a href="https://github.com/RyanBowie/copilot-studio-powerplatform-solution-reviewer-site/blob/main/LICENSE">LICENSE</a> · <a href="#top">Back to top ↑</a></p><p>Provided as is, without warranty of any kind. You're responsible for assessing, operating and securing anything you deploy from this site.</p>{extra}</footer>'''
