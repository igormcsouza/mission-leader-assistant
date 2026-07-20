"""Page object for the settings modal (#settingsModal)."""


class SettingsModal:
    """Wraps the ward + per-profile title/subtitle settings form."""

    def __init__(self, page):
        self.page = page

    def ward_value(self):
        return self.page.locator("#wardInput").input_value()

    def set_ward(self, ward):
        self.page.fill("#wardInput", ward)

    def switch_edit_profile(self, profile):
        self.page.click(f'.modal-slot-switcher .slot-btn[data-settings-profile="{profile}"]')

    def set_title(self, title):
        self.page.fill("#slotTitleInput", title)

    def set_subtitle(self, subtitle):
        self.page.fill("#slotSubtitleInput", subtitle)

    def save(self):
        self.page.click("#saveSettingsBtn")
        self.page.wait_for_selector("#settingsModal.hidden", state="attached")

    def cancel(self):
        self.page.click("#cancelSettingsBtn")
        self.page.wait_for_selector("#settingsModal.hidden", state="attached")
