"""Covers the per-week PDAY override ("P" button) and mute-day ("M" button) controls
that live alongside the core calendar rendering.
"""


def test_pday_override_moves_names_into_monday_preview(calendar_page):
    calendar_page.fill_name("Tuesday", "Familia Costa", slot=1)
    calendar_page.toggle_pday("Tuesday")

    assert "Familia Costa" in calendar_page.monday_preview_text()
    assert not calendar_page.monday_fixed_visible()


def test_pday_override_can_be_reverted_by_reselecting_monday(calendar_page):
    calendar_page.fill_name("Tuesday", "Familia Costa", slot=1)
    calendar_page.toggle_pday("Tuesday")
    calendar_page.toggle_pday("Monday")

    assert calendar_page.monday_fixed_visible()


def test_mute_toggle_disables_inputs_for_that_day(calendar_page):
    cell = calendar_page.day_cell("Wednesday")
    calendar_page.toggle_mute("Wednesday")

    assert "muted-active" in cell.locator(".cell").get_attribute("class")
    for i in range(cell.locator("input").count()):
        assert cell.locator("input").nth(i).is_disabled()


def test_mute_toggle_can_be_reverted(calendar_page):
    cell = calendar_page.day_cell("Wednesday")
    calendar_page.toggle_mute("Wednesday")
    calendar_page.toggle_mute("Wednesday")

    assert "muted-active" not in cell.locator(".cell").get_attribute("class")
