"""Regression tests tied to specific bug-fix commits."""


def test_clearing_a_cell_persists_as_empty(calendar_page, live_server):
    """Regression for commit b593f26: clearing a calendar field wasn't persisted,
    so a reload would still show the stale name instead of an empty cell."""
    calendar_page.fill_name("Thursday", "Familia Temporaria", slot=1)
    calendar_page.page.goto(live_server.base_url)
    calendar_page.page.wait_for_selector("#calendarView:not(.hidden)")
    assert calendar_page.name_input("Thursday", slot=1).input_value() == "Familia Temporaria"

    calendar_page.fill_name("Thursday", "", slot=1)
    calendar_page.page.goto(live_server.base_url)
    calendar_page.page.wait_for_selector("#calendarView:not(.hidden)")
    assert calendar_page.name_input("Thursday", slot=1).input_value() == ""


def test_long_names_do_not_overflow_the_cell(calendar_page):
    """Regression for commit 1bd7879: calendar cell height caused input overflow.

    This is an inherently fuzzy CSS assertion (bounding-box comparison), not a
    strict functional check.
    """
    long_name = "Familia Extremamente Nome Comprido De Teste"
    calendar_page.fill_name("Friday", long_name, slot=1)
    calendar_page.fill_name("Friday", long_name, slot=2)

    cell_box = calendar_page.day_cell("Friday").bounding_box()
    input_box = calendar_page.name_input("Friday", slot=2).bounding_box()

    assert input_box["y"] + input_box["height"] <= cell_box["y"] + cell_box["height"] + 1
