import logging
import time
from urllib.parse import urljoin

import pytest
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.usefixtures("setup", "logger")
class CustomBasePage:

    def __init__(self, browser, wait, base_url):
        self.browser = browser
        self.wait = wait
        self.base_url = base_url
        self.browser.set_page_load_timeout(60)

    def go_to_page(self, page_url):
        url = self.base_url + page_url
        print(f"CustomPage ________________base_url + page_url = {url}" )
        self.browser.get(url)

    def find_element(self, by_locator, timeout=10):
        return self.wait.until(EC.presence_of_element_located(by_locator), timeout)

    def element_visibility(self, by_locator, timeout=10):
        return self.wait.until(EC.visibility_of_element_located(by_locator), timeout)

    def visibility_of_all_elements(self, by_locator, timeout=10):
        return self.wait.until(EC.visibility_of_all_elements_located(by_locator), timeout)

    def find_all_elements(self, by_locator, timeout=10):
        return self.wait.until(EC.presence_of_all_elements_located(by_locator), timeout)

    def element_to_be_clickable(self, by_locator, timeout=10):
        return self.wait.until(EC.element_to_be_clickable(by_locator), timeout)

    def assert_element_text(self, by_locator, expected_text):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        assert element.text == expected_text

    def is_enabled(self, by_locator):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        return element.is_enabled()

    def enter_text(self, by_locator, text):
        return self.wait.until(EC.visibility_of_element_located(by_locator)).send_keys(text)

    def is_visible(self, by_locator):
        element = self.wait.until(EC.visibility_of_element_located(by_locator))
        return bool(element)

    def wait_for_long_load(self, by_locator, timeout=60):
        return self.wait.until(EC.visibility_of_element_located(by_locator), timeout)

    def wait_for_page_ready(self, timeout=10):
        """
        Waits until the page's readyState is 'complete', indicating that the page has finished loading.

        Args:
            timeout (int): Maximum time to wait for the page to be ready.

        Returns:
            bool: True if the page is ready within the timeout, False otherwise.
        """
        return self.wait.until(
            lambda driver: self.browser.execute_script("return document.readyState") == "complete",
            f"Page did not reach ready state within {timeout} seconds"
        )

    def wait_for_condition(self, condition, timeout=60, message=None):
        """
        General-purpose wait function to wait for a specific condition.
        :param condition: The condition to wait for (e.g., element presence, URL contains).
        :param timeout: How long to wait before timing out.
        :param message: Custom error message if timeout occurs.
        :return: The result of the condition (e.g., an element or True).
        """
        try:
            return self.wait.until(condition, message)
        except TimeoutException as e:
            raise RuntimeError(message or f"Condition not met within {timeout} seconds") from e

    def get_all_links(self):
        """Returns all valid absolute links from the page, handling relative URLs and hidden links."""
        try:
            # ✅ Ensure links and other elements are present before scraping
            self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            time.sleep(2)  # Allow additional time for dynamically loaded elements

            links = set()

            anchor_elements = self.browser.find_elements(By.TAG_NAME, "a")
            for a in anchor_elements:
                href = a.get_attribute("href")
                if href:
                    full_url = urljoin(self.base_url, href) if not href.startswith("http") else href
                    links.add(full_url)

            row_elements = self.browser.find_elements(By.XPATH, "//tr[@data-row-key]")
            for row in row_elements:
                row_link = row.get_attribute("data-row-key")
                if row_link:
                    full_url = urljoin(self.base_url, row_link) if not row_link.startswith("http") else row_link
                    links.add(full_url)

            button_elements = self.browser.find_elements(By.TAG_NAME, "button")
            for btn in button_elements:
                js_link = btn.get_attribute("onclick")
                if js_link and "http" in js_link:  # Extract links from JavaScript
                    extracted_url = js_link.split("'")[1] if "'" in js_link else js_link  # Handle different formats
                    full_url = urljoin(self.base_url, extracted_url) if not extracted_url.startswith(
                        "http") else extracted_url
                    links.add(full_url)

            self.logger.info(f"🔗 Found {len(links)} unique links on the page.")
            return list(links)

        except Exception as e:
            self.logger.error(f"❌ Error extracting links: {str(e)}")
            return []

