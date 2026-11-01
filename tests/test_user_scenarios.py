import pytest
from playwright.sync_api import Page, expect
from pages.main_page import MainPage

def test_main_page_interaction(page: Page, base_url: str):
    main_page = MainPage(page)
    main_page.open(base_url)
    main_page.check_header_visible()


def test_fetch_valid_cas_shows_label(page: Page, base_url: str):
    """Проверка генерации этикетки для цианида натрия (CAS 143-33-9)."""
    main_page = MainPage(page)
    main_page.open(base_url)
    
    # 1. Ввод данных
    main_page.search_by_cas("143-33-9")
    
    # 2. Проверка появления контента
    expect(page.get_by_text("Sodium Cyanide")).to_be_visible(timeout=10000)
    expect(main_page.hazard_level).to_be_visible()


@pytest.mark.parametrize("cas_number, expected_text", [
    ("67-56-1", "Methanol"),
    ("143-33-9", "Sodium Cyanide"),
])
def test_multiple_cas_inputs(page: Page, base_url: str, cas_number: str, expected_text: str):
    """Параметризованный тест: проверяет выдачу для нескольких веществ подряд."""
    main_page = MainPage(page)
    main_page.open(base_url)
    
    main_page.search_by_cas(cas_number)
    
    expect(page.get_by_text(expected_text)).to_be_visible(timeout=10000)