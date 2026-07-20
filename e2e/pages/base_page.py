"""Shared helpers for all page objects in the e2e suite."""


class BasePage:
    """Wraps a Playwright Page with drawer/navigation helpers common to every view."""

    def __init__(self, page):
        self.page = page

    def open_drawer(self):
        """Open the side navigation drawer via the hamburger button."""
        self.page.click("#menuToggleBtn")
        self.page.wait_for_selector("#sideDrawer.open")

    def close_drawer_via_backdrop(self):
        """Close the side navigation drawer by clicking outside it."""
        self.page.click("#drawerBackdrop")
        self.page.wait_for_selector("#sideDrawer:not(.open)")

    def navigate_to(self, route):
        """Open the drawer and click the nav item for the given route (e.g. "/baptismal-plan")."""
        self.open_drawer()
        self.page.click(f'.nav-item[data-route="{route}"]')
