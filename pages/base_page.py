from playwright.sync_api import Page, Response

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str) -> Response | None:
        return self.page.goto(url, wait_until="networkidle")

    def get_current_url(self) -> str:
        return self.page.url