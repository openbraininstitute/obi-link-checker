import logging
import time
from urllib.parse import urljoin

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.usefixtures("setup", "logger")
class BasePage:
    def __init__(self, browser, wait, base_url):
        self.browser = browser
        self.wait = wait
        self.base_url = base_url
        self.browser.set_page_load_timeout(60)
        self.logger = logging.getLogger(__name__)

    def go_to_page(self, page_url):
        url = urljoin(self.base_url, page_url)
        self.browser.get(url)

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

