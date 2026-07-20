"""Covers the calendar PNG export (`#downloadBtn`), a pure-canvas client-side feature
with no server/network dependency."""
import re


def test_download_produces_dated_png_and_status_message(calendar_page):
    calendar_page.fill_name("Tuesday", "Familia Lima", slot=1)

    download = calendar_page.download_png()

    assert re.fullmatch(r"calendar-\d{4}-\d{2}-\d{2}\.png", download.suggested_filename)
    assert download.suggested_filename in calendar_page.status_text()
