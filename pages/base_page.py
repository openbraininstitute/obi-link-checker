import logging

import pytest
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.usefixtures("setup", "logger")
class BasePage:
    def __init__(self, browser, wait, base_url):
        self.browser = browser
        self.wait = wait
        self.base_url = base_url
        self.browser.set_page_load_timeout(60)

    def go_to_page(self, page_url):
        url = self.base_url + page_url
        self.browser.get(url)


    def get_all_links(self):
        """Returns all valid links from the page"""
        links = [a.get_attribute("href") for a in self.browser.find_elements(By.TAG_NAME, "a") if a.get_attribute(
            "href")]
        logging.info(f"Found {len(links)} links on the page.")
        return links

    def wait_for_element(self, locator):
        """Waits for an element to be present"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def is_logged_in(self):
        """Checks if the user is still logged in."""
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "logout-button")))
            return True
        except TimeoutException:
            return False
