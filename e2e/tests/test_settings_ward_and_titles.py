"""Covers the ward name and per-profile title/subtitle settings (commit 496892f)."""
# pylint: disable=missing-function-docstring
from pages.settings_modal import SettingsModal


def test_settings_modal_prefills_current_ward(calendar_page):
    calendar_page.open_settings()
    modal = SettingsModal(calendar_page.page)
    assert modal.ward_value() == ""


def test_save_persists_ward_and_profile_title_after_reload(calendar_page, live_server):
    calendar_page.open_settings()
    modal = SettingsModal(calendar_page.page)
    modal.set_ward("Eusebio")
    modal.set_title("Calendario Customizado")
    modal.set_subtitle("Subtitulo customizado")
    modal.save()

    assert calendar_page.page.locator("#calendarTitle").text_content() == "Calendario Customizado"
    assert calendar_page.page.locator("#calendarSubtitle").text_content() == "Subtitulo customizado"

    calendar_page.page.goto(live_server.base_url)
    calendar_page.page.wait_for_selector("#calendarView:not(.hidden)")
    calendar_page.open_settings()
    assert SettingsModal(calendar_page.page).ward_value() == "Eusebio"


def test_cancel_discards_unsaved_edits(calendar_page):
    calendar_page.open_settings()
    modal = SettingsModal(calendar_page.page)
    modal.set_ward("Rascunho Nao Salvo")
    modal.cancel()

    calendar_page.open_settings()
    assert SettingsModal(calendar_page.page).ward_value() == ""
