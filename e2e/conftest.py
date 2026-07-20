"""Shared pytest fixtures for the Playwright e2e suite.

pytest inserts this directory (e2e/, which has no __init__.py) onto sys.path, which
is what makes `fixtures` and `pages` importable as top-level packages below.
"""
import pytest

# Re-exported so pytest can discover them as fixtures; also used directly below.
from fixtures.data import reset_data  # pylint: disable=unused-import
from fixtures.server import live_server  # pylint: disable=unused-import
from pages.baptismal_plan_page import BaptismalPlanPage
from pages.calendar_page import CalendarPage
from pages.side_drawer import SideDrawer


@pytest.fixture
# pytest fixtures conventionally shadow their own imported names; that's the
# whole mechanism, not a real name collision.
# pylint: disable=redefined-outer-name,unused-argument
def calendar_page(reset_data, live_server, page):
    """Load the app and return once dev-mode bootstrap has landed on the calendar view.

    Depends explicitly on `reset_data` (rather than relying on its autouse ordering)
    so the isolated data file is always wiped before this fixture's initial page load
    fetches anything — otherwise a same-session ordering race can let a later test's
    first fetch pick up data left behind by an earlier test.
    """
    page.goto(live_server.base_url)
    page.wait_for_selector("#calendarView:not(.hidden)")
    return CalendarPage(page)


@pytest.fixture
def baptismal_plan_page(calendar_page):  # pylint: disable=redefined-outer-name
    """Navigate from the calendar view into the baptismal plan view via the side drawer."""
    calendar_page.navigate_to("/baptismal-plan")
    calendar_page.page.wait_for_selector("#baptismalPlanView:not(.hidden)")
    return BaptismalPlanPage(calendar_page.page)


@pytest.fixture
def side_drawer(calendar_page):  # pylint: disable=redefined-outer-name
    """Return a SideDrawer bound to the same page as `calendar_page`."""
    return SideDrawer(calendar_page.page)


@pytest.fixture
def slow_network(page):
    """Add artificial latency to every request on `page` via CDP network emulation.

    A `page.route()` handler that blocks with `time.sleep()` seems like the obvious
    way to simulate a slow request, but it doesn't work here: Playwright's sync API
    runs on a single greenlet-based dispatcher thread, and a blocking sleep inside a
    route handler stalls that same thread — which also stalls every other Python-side
    Playwright call (including the ones a test would use to observe the resulting
    "loading" state) for the same duration. CDP-level throttling delays requests
    inside the browser process itself, so Python-side calls stay responsive.
    """
    session = page.context.new_cdp_session(page)
    session.send("Network.enable")
    session.send(
        "Network.emulateNetworkConditions",
        {"offline": False, "latency": 300, "downloadThroughput": -1, "uploadThroughput": -1},
    )
    yield
    session.send(
        "Network.emulateNetworkConditions",
        {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1},
    )
