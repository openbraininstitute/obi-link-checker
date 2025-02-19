import pytest
import requests
from selenium import webdriver
from pages.home_page import HomePage


@pytest.fixture(scope="session")
def driver():
    """Set up WebDriver (Chrome)"""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_broken_links(driver):
    """Test all links on the page for broken links"""
    home_page = HomePage(driver)
    home_page.open()
    links = home_page.get_all_links()

    assert links, "No links found on the page."

    for link in links:
        response = requests.head(link, allow_redirects=True)
        assert response.status_code < 400, f"Broken link: {link} returned {response.status_code}"
