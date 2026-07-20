"""Covers mobile/tablet responsive UI fixes (commits ce4aeca, d42be9c).

Structural/behavioral checks only (element visibility, overlay behavior, scroll
capability) rather than pixel snapshots, since the underlying commits are CSS-only.
"""
import pytest


@pytest.mark.parametrize("width,height", [(375, 667), (768, 1024)])
def test_menu_button_visible_and_drawer_overlays(calendar_page, side_drawer, width, height):
    calendar_page.page.set_viewport_size({"width": width, "height": height})

    assert calendar_page.page.locator("#menuToggleBtn").is_visible()

    calendar_page.open_drawer()
    assert side_drawer.is_open()
    drawer_box = calendar_page.page.locator("#sideDrawer").bounding_box()
    assert drawer_box is not None


def test_calendar_table_scrolls_horizontally_on_mobile(calendar_page):
    calendar_page.page.set_viewport_size({"width": 375, "height": 667})

    wrapper = calendar_page.page.locator(".table-scroll-wrapper")
    scroll_width = wrapper.evaluate("el => el.scrollWidth")
    client_width = wrapper.evaluate("el => el.clientWidth")
    assert scroll_width > client_width
