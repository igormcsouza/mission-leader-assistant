"""Covers the core lunch/visit calendar (commits f467a0d, 552e70d, e5a70ac): rendering,
saving both name slots, and the fixed/non-editable Monday "PDAY" cell.

Week 2 is used throughout because it is guaranteed to contain real (non-padding)
calendar days for any month (see CalendarPage docstring).
"""
from datetime import date

from fixtures.data import get_calendar_payload


def test_default_month_is_current_month(calendar_page):
    today = date.today()
    expected = f"{today.year:04d}-{today.month:02d}"
    assert calendar_page.page.locator("#monthPicker").input_value() == expected


def test_monday_is_locked_to_pday(calendar_page):
    monday = calendar_page.day_cell("Monday")
    assert monday.locator(".fixed-name").text_content().strip() == "PDAY"
    assert monday.locator("input").count() == 0


def test_two_name_slots_persist_independently_after_reload(calendar_page, live_server):
    calendar_page.fill_name("Tuesday", "Familia Silva", slot=1)
    calendar_page.fill_name("Tuesday", "Familia Souza", slot=2)

    calendar_page.page.goto(live_server.base_url)
    calendar_page.page.wait_for_selector("#calendarView:not(.hidden)")

    assert calendar_page.name_input("Tuesday", slot=1).input_value() == "Familia Silva"
    assert calendar_page.name_input("Tuesday", slot=2).input_value() == "Familia Souza"


def test_empty_padding_cells_render_without_inputs(calendar_page, context, live_server):
    # 2026-02 starts on a Sunday and has 28 days, so its display grid always has
    # trailing padding cells (day_number is null) in the later weeks.
    with calendar_page.page.expect_response(
        lambda r: "/api/calendar" in r.url and "month=2" in r.url
    ):
        calendar_page.page.fill("#monthPicker", "2026-02")
        calendar_page.page.dispatch_event("#monthPicker", "change")

    payload = get_calendar_payload(context.request, live_server.base_url, year=2026, month=2)
    # Monday always renders its fixed "PDAY" box regardless of day_number, so it
    # never shows `.empty-day` — exclude it and look for a genuine padding cell.
    empty_cell = next(
        cell
        for week in payload["weeks"]
        for cell in week["cells"]
        if cell["day_number"] is None and cell["day_of_week"] != "Monday"
    )

    dom_cell = calendar_page.day_cell(empty_cell["day_of_week"], week_number=empty_cell["week_number"])
    assert dom_cell.locator(".empty-day").is_visible()
    assert dom_cell.locator("input").count() == 0
