"""Page object for the lunch/visit calendar view (#calendarView)."""
# pylint: disable=missing-function-docstring
from .base_page import BasePage


class CalendarPage(BasePage):
    """Wraps interactions with the calendar table, profile switcher, and PNG export.

    Week 2 (rows are 1-indexed via `data-week-number`) always covers real calendar
    days ~2..14 of the month regardless of which weekday the month starts on, so it
    is used as the default "guaranteed populated" week across tests instead of week 1
    (which can contain empty padding cells depending on the month's start weekday).
    """

    def day_cell(self, day_of_week, week_number=2):
        row = f'tr[data-week-number="{week_number}"]'
        cell = f'td[data-day-of-week="{day_of_week}"]'
        return self.page.locator(f"#calendarBody {row} {cell}")

    def name_input(self, day_of_week, slot=1, week_number=2):
        cell = self.day_cell(day_of_week, week_number)
        selector = ".name-input.secondary" if slot == 2 else ".name-input:not(.secondary)"
        return cell.locator(selector)

    def fill_name(self, day_of_week, name, slot=1, week_number=2):
        field = self.name_input(day_of_week, slot, week_number)
        field.fill(name)
        field.blur()

    def switch_profile(self, profile):
        with self.page.expect_response(
            lambda r: "/api/calendar" in r.url and f"profile={profile}" in r.url
        ):
            self.page.click(f'#topbarSlotSwitcher .slot-btn[data-profile="{profile}"]')

    def active_profile_button(self):
        return self.page.locator("#topbarSlotSwitcher .slot-btn.active")

    def open_settings(self):
        self.page.click("#settingsBtn")
        self.page.wait_for_selector("#settingsModal:not(.hidden)")

    def download_png(self):
        with self.page.expect_download() as download_info:
            self.page.click("#downloadBtn")
        return download_info.value

    def toggle_pday(self, day_of_week, week_number=2):
        self.day_cell(day_of_week, week_number).locator(".pday-toggle").click()

    def toggle_mute(self, day_of_week, week_number=2):
        self.day_cell(day_of_week, week_number).locator(".mute-toggle").click()

    def monday_preview_text(self, week_number=2):
        return self.day_cell("Monday", week_number).locator(".monday-preview").text_content()

    def monday_fixed_visible(self, week_number=2):
        return self.day_cell("Monday", week_number).locator(".fixed-name").is_visible()

    def status_text(self):
        return self.page.locator("#statusText").text_content()
