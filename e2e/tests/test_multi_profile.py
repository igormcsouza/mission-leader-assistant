"""Covers multi-profile (Perfil) calendar management (commit 999ded9): two independent
calendars sharing the same UI, switched via the topbar slot buttons.
"""


def test_exactly_two_profile_buttons(calendar_page):
    assert calendar_page.page.locator("#topbarSlotSwitcher .slot-btn").count() == 2


def test_switching_profile_keeps_entries_independent(calendar_page):
    calendar_page.fill_name("Tuesday", "Perfil Um", slot=1)

    calendar_page.switch_profile(2)
    assert calendar_page.active_profile_button().get_attribute("data-profile") == "2"
    assert calendar_page.name_input("Tuesday", slot=1).input_value() == ""

    calendar_page.fill_name("Tuesday", "Perfil Dois", slot=1)

    calendar_page.switch_profile(1)
    assert calendar_page.name_input("Tuesday", slot=1).input_value() == "Perfil Um"

    calendar_page.switch_profile(2)
    assert calendar_page.name_input("Tuesday", slot=1).input_value() == "Perfil Dois"


def test_profile_outside_configured_range_is_rejected_by_the_api(context, live_server):
    response = context.request.get(
        f"{live_server.base_url}/api/calendar",
        headers={"X-User-Id": "local"},
        params={"year": "2026", "month": "1", "profile": "3"},
    )
    assert response.status == 400
    assert "profile must be between 1 and 2" in response.json()["error"]
