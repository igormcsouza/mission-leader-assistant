"""Per-test data isolation and API seeding helpers for the baptismal plan feature."""
import pytest

USER_HEADERS = {"X-User-Id": "local"}


@pytest.fixture(autouse=True)
def reset_data(live_server):
    """Delete both isolated data files before every test so each test starts clean.

    The calendar store and the baptismal-plan store write to two separate files
    (see LiveServer in fixtures/server.py) — both must be removed, or baptismal
    plan data leaks across tests. Both JsonFileStore classes re-read from disk on
    every call (no in-process cache), so this is safe without restarting the
    session-scoped server.
    """
    if live_server.data_file.exists():
        live_server.data_file.unlink()
    if live_server.baptismal_plan_data_file.exists():
        live_server.baptismal_plan_data_file.unlink()
    yield


def seed_baptismal_plan(request_context, base_url, payload=None):
    """Create a baptismal plan via the API, optionally updating it with `payload`.

    Bypasses the UI for tests that need pre-existing plans (e.g. switching between
    multiple plans) without depending on the create-plan flow under test elsewhere.
    """
    create_response = request_context.post(f"{base_url}/api/baptismal-plans", headers=USER_HEADERS, data={})
    assert create_response.ok, create_response.text()
    plan = create_response.json()["plan"]
    if payload:
        update_response = request_context.put(
            f"{base_url}/api/baptismal-plans/{plan['id']}",
            headers=USER_HEADERS,
            data=payload,
        )
        assert update_response.ok, update_response.text()
        plan = update_response.json()["plan"]
    return plan


def get_calendar_payload(request_context, base_url, year, month, profile=1):
    """Fetch the raw /api/calendar JSON payload for the given month, as the app itself would."""
    response = request_context.get(
        f"{base_url}/api/calendar",
        headers=USER_HEADERS,
        params={"year": str(year), "month": str(month), "profile": str(profile)},
    )
    assert response.ok, response.text()
    return response.json()
