"""Small standalone UI facts: dark theme (commit 552e70d, static CSS only — no toggle
exists in the current UI) and favicon/branding (commit 857dded).
"""
# pylint: disable=missing-function-docstring


def test_dark_theme_background_and_form_controls(calendar_page):
    bg_var = calendar_page.page.evaluate(
        "getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()"
    )
    assert bg_var == "#0c121b"

    month_picker_color_scheme = calendar_page.page.evaluate(
        "getComputedStyle(document.getElementById('monthPicker')).colorScheme"
    )
    assert month_picker_color_scheme == "dark"


def test_page_title(calendar_page):
    assert calendar_page.page.title() == "Assistente da Obra Missionária"


def test_favicon_link_and_asset(calendar_page, live_server, context):
    href = calendar_page.page.locator('link[rel="icon"]').get_attribute("href")
    assert href == "/favicon.svg"

    response = context.request.get(f"{live_server.base_url}{href}")
    assert response.ok
    assert "svg" in response.headers.get("content-type", "")
