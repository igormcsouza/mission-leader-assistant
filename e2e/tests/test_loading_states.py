"""Covers loading-state indicators added for auth/API calls (commit 8bd0b8d): the
calendar status spinner and the baptismal-plan autosave status text.

Both tests use the `slow_network` fixture (CDP-level request throttling) to create
a window in which the transient "loading" state can be observed.
"""
# pylint: disable=missing-function-docstring,unused-argument


def test_calendar_spinner_shows_while_initial_data_loads(slow_network, live_server, page):
    page.goto(live_server.base_url)

    page.wait_for_selector("#statusSpinner:not(.hidden)")
    page.wait_for_selector("#statusSpinner.hidden", state="attached", timeout=5000)


def test_baptismal_plan_save_status_transitions_while_saving(slow_network, baptismal_plan_page):
    baptismal_plan_page.new_plan()

    # Trigger the save directly (not via fill_details, which waits for the save
    # response before returning) so there is a window to observe "Salvando…".
    page = baptismal_plan_page.page
    page.fill("#bpWard", "Ala com Atraso")
    page.locator("#bpWard").blur()

    page.wait_for_function(
        "document.getElementById('bpSaveStatus').textContent === 'Salvando…'"
    )
    baptismal_plan_page.wait_for_saved()
