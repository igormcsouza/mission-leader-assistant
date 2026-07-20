"""Covers the Baptismal Plan (Planejamento Batismal) CRUD feature (commit 6107848):
create/edit/delete plans, candidates, and reload persistence.
"""
# pylint: disable=missing-function-docstring
from fixtures.data import seed_baptismal_plan
from pages.baptismal_plan_page import BaptismalPlanPage
from pages.calendar_page import CalendarPage


def test_empty_state_shown_with_no_plans(baptismal_plan_page):
    assert baptismal_plan_page.empty_state_visible()
    assert not baptismal_plan_page.editor_visible()


def test_new_plan_appears_in_list_with_default_status(baptismal_plan_page):
    baptismal_plan_page.new_plan()

    assert baptismal_plan_page.editor_visible()
    items = baptismal_plan_page.plan_items()
    assert items.count() == 1
    assert "Rascunho" in items.first.text_content()
    assert "Sem candidatos" in items.first.text_content()


def test_editing_details_autosaves(baptismal_plan_page):
    baptismal_plan_page.new_plan()
    baptismal_plan_page.fill_details(
        service_date="2026-08-15", ward="Eusebio", status="Scheduled"
    )

    assert "Agendado" in baptismal_plan_page.plan_items().first.text_content()


def test_add_candidate_autosaves_and_populates_ordinances_section(baptismal_plan_page):
    baptismal_plan_page.new_plan()
    assert baptismal_plan_page.ordinances_witnesses_empty_note_visible()

    baptismal_plan_page.add_candidate()
    assert baptismal_plan_page.candidate_cards().count() == 1
    assert not baptismal_plan_page.ordinances_witnesses_empty_note_visible()

    baptismal_plan_page.fill_candidate(0, full_name="Joao Silva", candidate_type="Convert")
    assert "Joao Silva" in baptismal_plan_page.plan_items().first.text_content()


def test_remove_candidate_autosaves(baptismal_plan_page):
    baptismal_plan_page.new_plan()
    baptismal_plan_page.add_candidate()

    baptismal_plan_page.remove_candidate(0)
    assert baptismal_plan_page.candidate_cards().count() == 0
    assert baptismal_plan_page.ordinances_witnesses_empty_note_visible()


def test_delete_plan_removes_it_and_shows_empty_state(baptismal_plan_page):
    baptismal_plan_page.new_plan()
    plan_id = baptismal_plan_page.plan_items().first.get_attribute("data-plan-id")

    baptismal_plan_page.delete_plan(plan_id)
    baptismal_plan_page.page.wait_for_selector("#bpEmptyState:not(.hidden)")

    assert baptismal_plan_page.plan_items().count() == 0
    assert baptismal_plan_page.empty_state_visible()


def test_switching_between_existing_plans_loads_correct_data(calendar_page, context, live_server):
    plan_a = seed_baptismal_plan(
        context.request, live_server.base_url, {"serviceDate": "2026-01-10", "ward": "Ala A"}
    )
    plan_b = seed_baptismal_plan(
        context.request, live_server.base_url, {"serviceDate": "2026-02-20", "ward": "Ala B"}
    )

    calendar_page.navigate_to("/baptismal-plan")
    calendar_page.page.wait_for_selector("#baptismalPlanView:not(.hidden)")
    bp_page = BaptismalPlanPage(calendar_page.page)

    bp_page.select_plan(plan_a["id"])
    assert bp_page.page.locator("#bpWard").input_value() == "Ala A"

    bp_page.select_plan(plan_b["id"])
    assert bp_page.page.locator("#bpWard").input_value() == "Ala B"


def test_reload_persists_plan_data(baptismal_plan_page, live_server):
    baptismal_plan_page.new_plan()
    plan_id = baptismal_plan_page.plan_items().first.get_attribute("data-plan-id")
    baptismal_plan_page.fill_details(ward="Ala Persistente")

    page = baptismal_plan_page.page
    page.goto(live_server.base_url)
    page.wait_for_selector("#calendarView:not(.hidden)")
    CalendarPage(page).navigate_to("/baptismal-plan")
    page.wait_for_selector("#baptismalPlanView:not(.hidden)")

    reloaded = BaptismalPlanPage(page)
    reloaded.select_plan(plan_id)
    assert page.locator("#bpWard").input_value() == "Ala Persistente"
