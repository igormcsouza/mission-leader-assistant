"""Covers the collapsible side navigation drawer (commit 85ebcd9)."""
# pylint: disable=missing-function-docstring,unused-argument


def test_drawer_starts_closed(calendar_page, side_drawer):
    assert not side_drawer.is_open()


def test_menu_button_opens_and_backdrop_closes_drawer(calendar_page, side_drawer):
    calendar_page.open_drawer()
    assert side_drawer.is_open()

    calendar_page.close_drawer_via_backdrop()
    assert not side_drawer.is_open()


def test_nav_items_are_calendar_and_baptismal_plan(side_drawer, calendar_page):
    calendar_page.open_drawer()
    labels = [label.strip() for label in side_drawer.nav_item_labels()]
    assert labels == ["Calendário", "Planejamento Batismal"]


def test_navigating_switches_view_and_closes_drawer(calendar_page, side_drawer):
    calendar_page.navigate_to("/baptismal-plan")

    assert calendar_page.page.locator("#baptismalPlanView").is_visible()
    assert calendar_page.page.locator("#calendarView").is_hidden()
    assert not side_drawer.is_open()
    assert side_drawer.active_route() == "/baptismal-plan"


def test_dev_mode_sign_out_closes_drawer_without_error(calendar_page, side_drawer):
    calendar_page.open_drawer()
    side_drawer.sign_out()

    assert not side_drawer.is_open()
    assert calendar_page.page.locator("#calendarView").is_visible()
