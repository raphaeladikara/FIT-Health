import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen

from web.serve_live import LiveHandler


def test_live_server_serves_static_pages_and_assessment_api():
    server = ThreadingHTTPServer(("127.0.0.1", 0), LiveHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert urlopen(f"{base}/").status == 200
        assert urlopen(f"{base}/dashboard.html").status == 200
        assert urlopen(f"{base}/assessment.html").status == 200
        request = Request(
            f"{base}/api/assess",
            data=b'{"mode":"PRE_LAB","values":{}}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        response = urlopen(request)
        payload = json.loads(response.read())
        assert response.status == 200
        assert response.headers["Cache-Control"] == "no-store"
        assert payload["abstention"]["required"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
