"""Generate the single approved current-case data source without any runtime action."""
import json
from pathlib import Path
from build_walkthrough import verify, primary_content

site = Path(__file__).resolve().parents[1]
c = json.loads((site / "content.json").read_text(encoding="utf-8"))
if c["downloads"]["installerIncluded"] or not c["historicalExample"]["approvedPublicDerivatives"]:
    raise ValueError("Only reviewed derivatives may be enabled; historical evidence must remain approved.")
c["example"] = primary_content(verify())
(site / "content.json").write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(site / "content.js").write_text("window.PSR_CONTENT = " + json.dumps(c, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
