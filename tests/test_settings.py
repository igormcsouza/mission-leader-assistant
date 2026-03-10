"""Tests for the settings module (constants) and the settings API endpoints."""
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from core.store import JsonFileStore  # noqa: E402  # pylint: disable=wrong-import-position
from handlers.calendar_handler import CalendarHandler  # noqa: E402  # pylint: disable=wrong-import-position
from settings import (  # noqa: E402  # pylint: disable=wrong-import-position
    DATA_FILE,
    DEFAULT_HOST,
    DEFAULT_PORT,
    MAX_APP_PROFILES,
)


def _make_handler(method, path, body=None, headers=None):
    """Return a CalendarHandler instance wired to in-memory streams."""
    raw_headers = {"X-User-Id": "testuser"}
    if headers:
        raw_headers.update(headers)

    body_bytes = json.dumps(body).encode() if body else b""
    if body_bytes:
        raw_headers["Content-Length"] = str(len(body_bytes))

    rfile = io.BytesIO(body_bytes)
    wfile = io.BytesIO()

    handler = CalendarHandler.__new__(CalendarHandler)
    handler.rfile = rfile
    handler.wfile = wfile
    handler.headers = raw_headers
    handler.path = path
    handler.requestline = f"{method} {path} HTTP/1.1"
    handler.request_version = "HTTP/1.1"
    handler.server = type("FakeServer", (), {"server_name": "localhost", "server_port": 5001})()
    handler.client_address = ("127.0.0.1", 9999)
    return handler, wfile


def _parse_response(wfile):
    """Parse raw HTTP response bytes into (status_code, payload_dict)."""
    wfile.seek(0)
    raw = wfile.read().decode("utf-8", errors="replace")
    lines = raw.split("\r\n")
    status_code = int(lines[0].split(" ")[1])
    body_start = raw.find("\r\n\r\n") + 4
    payload = json.loads(raw[body_start:])
    return status_code, payload


class TestSettingsConstants(unittest.TestCase):
    """Tests for the configuration constants exported from settings.py."""

    def test_default_host(self):
        """DEFAULT_HOST is the all-interfaces bind address."""
        self.assertEqual(DEFAULT_HOST, "0.0.0.0")

    def test_default_port(self):
        """DEFAULT_PORT is a valid TCP port number."""
        self.assertIsInstance(DEFAULT_PORT, int)
        self.assertGreater(DEFAULT_PORT, 0)
        self.assertLessEqual(DEFAULT_PORT, 65535)

    def test_data_file_is_json(self):
        """DATA_FILE ends with .json."""
        self.assertTrue(DATA_FILE.endswith(".json"))

    def test_max_app_profiles_is_two(self):
        """MAX_APP_PROFILES is 2."""
        self.assertEqual(MAX_APP_PROFILES, 2)


class TestSettingsGetEndpoint(unittest.TestCase):
    """Tests for GET /api/settings via CalendarHandler."""

    def setUp(self):
        self._fd, self._tmp = tempfile.mkstemp(suffix=".json")
        os.close(self._fd)
        CalendarHandler.STORE = JsonFileStore(self._tmp)
        CalendarHandler.LOGGED_USER_IDS.clear()

    def tearDown(self):
        for path in (self._tmp, self._tmp.replace(".json", "_settings.json")):
            if os.path.exists(path):
                os.unlink(path)

    def test_returns_empty_settings_for_new_user(self):
        """GET /api/settings returns an empty dict for a user with no stored settings."""
        handler, wfile = _make_handler("GET", "/api/settings")
        handler.do_GET()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["settings"], {})

    def test_returns_stored_settings(self):
        """GET /api/settings returns previously saved settings."""
        CalendarHandler.STORE.save_settings("testuser", {"ward": "Westside"})
        handler, wfile = _make_handler("GET", "/api/settings")
        handler.do_GET()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 200)
        self.assertEqual(payload["settings"]["ward"], "Westside")

    def test_missing_user_id_returns_401(self):
        """GET /api/settings without X-User-Id returns 401."""
        handler, wfile = _make_handler("GET", "/api/settings", headers={"X-User-Id": ""})
        handler.do_GET()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 401)
        self.assertEqual(payload["status"], "error")


class TestSettingsPostEndpoint(unittest.TestCase):
    """Tests for POST /api/settings via CalendarHandler."""

    def setUp(self):
        self._fd, self._tmp = tempfile.mkstemp(suffix=".json")
        os.close(self._fd)
        CalendarHandler.STORE = JsonFileStore(self._tmp)
        CalendarHandler.LOGGED_USER_IDS.clear()

    def tearDown(self):
        for path in (self._tmp, self._tmp.replace(".json", "_settings.json")):
            if os.path.exists(path):
                os.unlink(path)

    def test_saves_ward(self):
        """POST /api/settings persists the ward and returns it."""
        handler, wfile = _make_handler("POST", "/api/settings", body={"ward": "Northfield"})
        handler.do_POST()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 200)
        self.assertEqual(payload["settings"]["ward"], "Northfield")

    def test_clears_ward_with_empty_string(self):
        """POST /api/settings with an empty ward removes the key."""
        CalendarHandler.STORE.save_settings("testuser", {"ward": "Northfield"})
        handler, wfile = _make_handler("POST", "/api/settings", body={"ward": ""})
        handler.do_POST()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 200)
        self.assertNotIn("ward", payload["settings"])

    def test_saves_profile_title(self):
        """POST /api/settings saves a per-profile title field."""
        handler, wfile = _make_handler(
            "POST", "/api/settings", body={"slot_1_title": "Elders"}
        )
        handler.do_POST()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 200)
        self.assertEqual(payload["settings"]["slot_1_title"], "Elders")

    def test_missing_user_id_returns_401(self):
        """POST /api/settings without X-User-Id returns 401."""
        handler, wfile = _make_handler(
            "POST", "/api/settings", body={"ward": "X"}, headers={"X-User-Id": ""}
        )
        handler.do_POST()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 401)
        self.assertEqual(payload["status"], "error")

    def test_invalid_json_returns_400(self):
        """POST /api/settings with invalid JSON returns 400."""
        handler, wfile = _make_handler("POST", "/api/settings")
        # Replace rfile with raw invalid bytes after construction.
        handler.rfile = io.BytesIO(b"notjson")
        handler.headers["Content-Length"] = "7"
        handler.do_POST()
        status, payload = _parse_response(wfile)
        self.assertEqual(status, 400)
        self.assertEqual(payload["status"], "error")


if __name__ == "__main__":
    unittest.main()
