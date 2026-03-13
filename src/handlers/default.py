"""Base HTTP request handler providing shared utilities."""
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from core.logger import LOGGER


class DefaultHandler(BaseHTTPRequestHandler):
    """Base handler with shared JSON helpers, static-file serving, and auth utilities."""

    LOGGED_USER_IDS: set = set()

    # ── auth ─────────────────────────────────────────────────────────────────

    def get_user_id(self):
        """Extract and return the authenticated user ID from request headers."""
        user_id = self.headers.get("X-User-Id", "").strip()
        if not user_id:
            return None
        if user_id not in self.LOGGED_USER_IDS:
            self.LOGGED_USER_IDS.add(user_id)
            LOGGER.info("Authenticated user uid=%s", user_id)
        return user_id

    # ── response helpers ──────────────────────────────────────────────────────

    def send_json(self, status_code, payload):
        """Serialize payload as JSON and send an HTTP response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, filename, content_type):
        """Serve a static file from the views directory."""
        file_path = Path(__file__).parent.parent / "views" / filename
        if not file_path.exists():
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"{filename} not found".encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def send_index(self):
        """Serve the index.html file."""
        self.send_static("index.html", "text/html; charset=utf-8")

    # ── request parsing ───────────────────────────────────────────────────────

    def _parse_json_body(self):
        """Read and parse the JSON request body.

        Returns the parsed dict on success, or None after sending a 400 response
        when the body is missing or contains invalid JSON.
        """
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            self.send_json(400, {"status": "error", "error": "Invalid JSON"})
            return None

    def _require_authenticated_json(self):
        """Authenticate the request and parse the JSON body.

        Returns ``(user_id, data)`` on success.  On failure, sends the
        appropriate error response (401 or 400) and returns ``(None, None)``.
        """
        user_id = self.get_user_id()
        if not user_id:
            self.send_json(401, {"status": "error", "error": "User not authenticated"})
            return None, None
        data = self._parse_json_body()
        if data is None:
            return None, None
        return user_id, data

    # ── logging ───────────────────────────────────────────────────────────────

    def log_message(self, _fmt, *args):  # pylint: disable=arguments-differ
        """Suppress default HTTP server console logging; use the custom LOGGER instead."""

    # ── default routing ───────────────────────────────────────────────────────

    def do_GET(self):  # pylint: disable=invalid-name
        """Return 404 for any unhandled GET request."""
        self.send_json(404, {"status": "error", "error": "Not found"})

    def do_POST(self):  # pylint: disable=invalid-name
        """Return 404 for any unhandled POST request."""
        self.send_json(404, {"status": "error", "error": "Not found"})
