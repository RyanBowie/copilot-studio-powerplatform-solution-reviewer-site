"""Generate the single approved current-case data source without any runtime action."""
import json
from pathlib import Path
from build_walkthrough import verify, primary_content
from word_release import verify as verify_word_release, summary as word_summary

site = Path(__file__).resolve().parents[1]
c = json.loads((site / "content.json").read_text(encoding="utf-8"))
release = verify_word_release(site, required=c["downloads"]["installerIncluded"])
if not c["historicalExample"]["approvedPublicDerivatives"]:
    raise ValueError("Historical evidence must remain approved.")
c["example"] = primary_content(verify())
if release:
    c["wordOutput"] = word_summary(release)
    c["downloads"].update(
        installerIncluded=True,
        status="Reviewed Word-output configure-before-import solution bundle, matching template and redacted example. Historical TXT/JSON/Markdown evidence is retained unchanged. No credentials or working demo bindings are shipped.",
    )
    c["publication"]["scope"] = "Reviewed Word-output release and redacted synthetic format example, alongside unchanged matched real-canvas/email walkthrough and historical evidence."
(site / "content.json").write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(site / "content.js").write_text("window.PSR_CONTENT = " + json.dumps(c, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
