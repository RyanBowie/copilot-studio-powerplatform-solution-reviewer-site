"""Serve only the approved candidate allowlist on loopback, never private material."""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse, quote

SITE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=4178)
parser.add_argument("--base-path", default="/preview/")
args = parser.parse_args()
if not args.base_path.startswith("/") or not args.base_path.endswith("/"):
    raise SystemExit("Use a leading and trailing slash for the local path.")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *values, **kwargs):
        super().__init__(*values, directory=str(SITE), **kwargs)

    def send_head(self):
        path = unquote(urlparse(self.path).path)
        if not path.startswith(args.base_path):
            self.send_error(404)
            return None
        relative = path[len(args.base_path):] or "index.html"
        m = json.loads((SITE / "PUBLICATION-MANIFEST.json").read_text(encoding="utf-8"))
        if relative not in m["exactDeploymentAllowlist"]:
            self.send_error(404)
            return None
        self.path = "/" + quote(relative)
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *_):
        pass


print("Allowlisted local candidate preview only; no hosting/publication action.", flush=True)
ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
