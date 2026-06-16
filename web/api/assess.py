"""Vercel-compatible JSON-only assessment endpoint."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import traceback
from typing import Any

from .inference import LockedInferenceService
from .validation import AssessmentValidationError


MAX_REQUEST_BYTES = 64 * 1024
_SERVICE: LockedInferenceService | None = None


def get_service() -> LockedInferenceService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = LockedInferenceService(Path(__file__).resolve().parents[1])
    return _SERVICE


def handle_assessment(
    body: bytes,
    content_type: str,
    *,
    service: LockedInferenceService | None = None,
) -> tuple[int, dict[str, str], dict[str, Any]]:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
    }
    if content_type.split(";")[0].strip().lower() != "application/json":
        return 415, headers, {"error": "JSON content type required"}
    if len(body) > MAX_REQUEST_BYTES:
        return 413, headers, {"error": "Request is too large"}
    try:
        payload = json.loads(body.decode("utf-8"))
        if set(payload) != {"mode", "values"}:
            raise AssessmentValidationError(
                "request must contain only mode and values"
            )
        response = (service or get_service()).assess(
            str(payload["mode"]), payload["values"]
        )
        if response["abstention"]["reasons"] == ["UNSUPPORTED_MODE"]:
            return 400, headers, response
        return 200, headers, response
    except AssessmentValidationError as exc:
        return 400, headers, {
            "error": "Invalid assessment input",
            "field_errors": exc.field_errors or {},
        }
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError):
        return 400, headers, {"error": "Invalid assessment input"}
    except ValueError:
        return 409, headers, {"error": "Model version is incompatible"}
    except Exception:
        traceback.print_exc()
        return 500, headers, {"error": "Assessment could not be completed"}


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
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

    def log_message(self, format: str, *args) -> None:
        return
