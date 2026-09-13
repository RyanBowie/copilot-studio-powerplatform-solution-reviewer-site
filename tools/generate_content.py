"""Generate the single approved current-case data source without any runtime action."""
import json
from pathlib import Path

site = Path(__file__).resolve().parents[1]
c = json.loads((site / "content.json").read_text(encoding="utf-8"))
if c["downloads"]["installerIncluded"] or not c["example"]["approvedPublicDerivatives"]:
    raise ValueError("Only the approved real-case public derivatives may be enabled.")
(site / "content.js").write_text("window.PSR_CONTENT = " + json.dumps(c, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
