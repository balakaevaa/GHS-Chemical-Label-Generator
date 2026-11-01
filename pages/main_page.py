from playwright.sync_api import Page, expect
from pages.base_page import BasePage

class MainPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Локаторы основных элементов
        self.header_title = page.get_by_role("heading", name="GHS Label Generator")
        self.cas_input = page.get_by_placeholder("e.g. 67-56-1")
        self.fetch_button = page.get_by_role("button", name="Fetch")
        
        # Локаторы для проверки результатов
        self.hazard_level = page.get_by_text("DANGER", exact=True)
        self.chemical_name = page.locator("strong:has-text('CAS:') + *") 

    def search_by_cas(self, cas_code: str):
        """Очищает поле, вводит CAS и нажимает Fetch."""
        self.cas_input.fill(cas_code)
        self.fetch_button.click()

    def check_header_visible(self):
        expect(self.header_title).to_be_visible()