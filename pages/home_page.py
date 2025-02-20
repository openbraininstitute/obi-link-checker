import logging
import time

import os
import time
import logging
from pages.base_page import BasePage
from pages.login_page import LoginPage


class HomePage(BasePage):
    def __init__(self, browser, wait, base_url):
        super().__init__(browser, wait, base_url)
        self.logger = logging.getLogger(__name__)
        self.lab_id = "37a3a2e8-a4b4-456b-8aff-4e23e87a5cbc"
        self.project_id = "8abcb1e3-b714-4267-a22c-3b3dc4be5306"
        self.pages = []

    def go_to_home_page(self):
        """Navigates to the homepage."""
        self.go_to_page("")
        self.logger.info("🏠 Navigated to homepage.")

    def login_and_scrape(self):
        """Logs in before scraping all pages."""
        self.logger.info("🔄 Logging in before scraping...")

        login_page = LoginPage(self.browser, self.wait, self.base_url)
        login_page.navigate_to_homepage()
        login_page.login()

        if "login" in self.browser.current_url:
            self.logger.error("❌ Login failed: Still on login page!")
            raise Exception("Login failed!")

        if self.browser.current_url == self.base_url:
            self.logger.warning("⚠️ Redirected back to base_url. Navigating to virtual lab manually.")
            self.browser.get(f"{self.base_url}/virtual-lab")

        self.logger.info("✅ Login successful, ready to scrape.")

    def get_all_links_from_all_pages(self):
        """Extracts all links from all pages."""
        if not self.pages:
            self.logger.warning("⚠️ No pages defined for scraping.")
            return []

        all_links = set()
        self.logger.info(f"📌 Starting link extraction. Total pages: {len(self.pages)}")

        for page in self.pages:
            full_url = page
            self.logger.info(f"➡️ Navigating to: {full_url}")
            self.go_to_page(full_url)
            time.sleep(2)

            current_url = self.browser.current_url
            self.logger.info(f"✅ Arrived at: {current_url}")

            if not self.is_logged_in():
                self.logger.warning(f"🚨 Lost session before reaching {full_url}. Logging in again...")
                login_page = LoginPage(self.browser, self.wait, self.base_url)
                login_page.go_to_page()
                login_page.login()

                if not self.is_logged_in():
                    self.logger.error("❌ Login failed after session loss. Stopping execution.")
                    raise Exception("Login failure detected!")

                self.logger.info(f"🔄 Re-navigating to: {full_url} after re-login")
                self.go_to_page(full_url)
                time.sleep(2)

            links = self.get_all_links()
            self.logger.info(f"🔗 Found {len(links)} links on {full_url}")
            all_links.update(links)

        self.logger.info(f"✅ Total unique links found: {len(all_links)}")
        return list(all_links)


