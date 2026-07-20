"""Covers dev-mode auth bypass (commits 45e3799, e4ec5c7): the app skips Firebase
login entirely when `--dev` is set, using a hardcoded "local" user identity.
"""


def test_api_config_reports_dev_mode(context, live_server):
    response = context.request.get(f"{live_server.base_url}/api/config")
    assert response.ok
    assert response.json() == {"dev": True}


def test_login_view_is_skipped(calendar_page):
    assert calendar_page.page.locator("#loginView").is_hidden()
    assert calendar_page.page.locator("#appNavBar").is_visible()
    assert calendar_page.page.locator("#calendarView").is_visible()


def test_drawer_shows_local_user(calendar_page, side_drawer):
    calendar_page.open_drawer()
    assert side_drawer.user_name().strip() == "local"


def test_api_calls_carry_local_user_header(live_server, page):
    requests = []
    page.on("request", lambda request: requests.append(request))

    page.goto(live_server.base_url)
    page.wait_for_selector("#calendarView:not(.hidden)")

    calendar_requests = [req for req in requests if "/api/calendar" in req.url]
    assert calendar_requests
    assert calendar_requests[0].headers.get("x-user-id") == "local"
