"""Serve static VECTRA-X files and the locked local assessment API."""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import time

try:
    from .api.assess import MAX_REQUEST_BYTES, handle_assessment
except ImportError:  # direct script execution from web/
    from api.assess import MAX_REQUEST_BYTES, handle_assessment


WEB_ROOT = Path(__file__).resolve().parent


class LiveHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def list_directory(self, path):
        self.send_error(404)
        return None

    def do_POST(self):
        started = time.perf_counter()
        status = 404
        if self.path == "/api/assess":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(min(length, MAX_REQUEST_BYTES + 1))
            status, headers, payload = handle_assessment(
                body, self.headers.get("Content-Type", "")
            )
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        else:
            self.send_error(status)
        duration = (time.perf_counter() - started) * 1000
        print(f"POST {self.path} {status} {duration:.1f}ms")

    def log_message(self, format, *args):
        if args and str(args[0]).startswith('"POST'):
            return
        super().log_message(format, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), LiveHandler)
    print(f"VECTRA-X live demo: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
