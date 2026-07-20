"""Page object for the side navigation drawer (#sideDrawer)."""
# pylint: disable=missing-function-docstring


class SideDrawer:
    """Wraps the collapsible navigation drawer and its footer user panel."""

    def __init__(self, page):
        self.page = page

    def is_open(self):
        classes = self.page.locator("#sideDrawer").get_attribute("class") or ""
        return "open" in classes.split()

    def nav_item_labels(self):
        return self.page.locator("#sideDrawer .nav-item").all_inner_texts()

    def active_route(self):
        return self.page.locator("#sideDrawer .nav-item.active").get_attribute("data-route")

    def user_name(self):
        return self.page.locator("#drawerUserName").text_content()

    def sign_out(self):
        self.page.click("#drawerSignOutBtn")
