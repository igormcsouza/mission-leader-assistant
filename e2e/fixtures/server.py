"""Subprocess lifecycle management for the live app server used by e2e tests."""
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ENTRYPOINT = REPO_ROOT / "src" / "app.py"
READY_TIMEOUT_SECONDS = 10
READY_POLL_INTERVAL_SECONDS = 0.1


@dataclass
class LiveServer:
    """A running instance of the app, started in --dev mode for e2e tests."""

    base_url: str
    process: subprocess.Popen
    data_file: Path
    baptismal_plan_data_file: Path


def _free_port() -> int:
    """Return a currently-unused TCP port by binding to port 0 and releasing it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_ready(process: subprocess.Popen, config_url: str) -> None:
    """Poll `config_url` until it responds or the process exits/times out."""
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"App server exited early (code {process.returncode}):\n{output}")
        try:
            with urllib.request.urlopen(config_url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError):
            pass
        time.sleep(READY_POLL_INTERVAL_SECONDS)
    process.kill()
    output = process.stdout.read() if process.stdout else ""
    raise RuntimeError(f"App server did not become ready in time:\n{output}")


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    """Start the app once for the whole test session, isolated from the developer's real data.

    The data file resolves relative to the process CWD (see JsonFileStore in
    src/core/store.py), so launching with cwd set to a throwaway temp dir keeps
    e2e runs from ever touching the real calendar_data.json.
    """
    data_dir = tmp_path_factory.mktemp("e2e-data")
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    process = subprocess.Popen(  # pylint: disable=consider-using-with
        [sys.executable, str(APP_ENTRYPOINT), "--dev", "--host", "127.0.0.1", "--port", str(port)],
        cwd=data_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    _wait_until_ready(process, base_url + "/api/config")

    # BaptismalPlanJsonStore writes to a sibling "<stem>_baptismal_plans.<ext>" file
    # rather than calendar_data.json itself (see create_baptismal_plan_store in
    # src/core/store.py) — both must be tracked so tests can reset both stores.
    yield LiveServer(
        base_url=base_url,
        process=process,
        data_file=data_dir / "calendar_data.json",
        baptismal_plan_data_file=data_dir / "calendar_data_baptismal_plans.json",
    )

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
