# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0


import time
import logging
from pages.base_page import CustomBasePage
from pages.urls import get_dynamic_pages


class HomePage(CustomBasePage):
    def __init__(self, browser, wait, base_url, logger):
        super().__init__(browser, wait, base_url, logger)
        self.logger = logging.getLogger(__name__)
        self.lab_id = "d8f2d02a-05b9-4e25-8f68-45b7d8818703"
        self.project_id = "8fd987ca-8f05-497b-939f-c77027ddd004"
        self.pages = get_dynamic_pages(base_url,self.lab_id, self.project_id)
        self.logger = logger

    def go_to_home_page(self):
        """Navigates to the homepage."""
        self.go_to_page("")
        self.logger.info("Navigated to homepage.")

    def login_and_scrape(self, login_fixture):
        """Logs in before scraping all pages."""
        self.logger.info("Logging in before scraping...")

        if not self.is_logged_in():
            self.logger.info("Not logged in, attempting to log in...")
            browser, wait = login_fixture
            if "login" in self.browser.current_url:
                self.logger.error("❌ Login failed: Still on login page!")
                raise Exception("Login failed!")

            if self.browser.current_url == self.base_url:
                self.logger.warning("⚠️ Redirected back to base_url. Navigating to virtual lab manually.")
                self.browser.get(f"{self.base_url}")
            self.logger.info("✅ Login successful, ready to scrape.")
        else:
            self.logger.info("🔄 Already logged in, proceeding with scraping.")
        return self.get_all_links_from_all_pages(login_fixture)

    def get_all_links_from_all_pages(self, login_fixture):
        """Extracts all links from all pages."""
        if not self.pages:
            self.logger.warning("⚠️ No pages defined for scraping.")
            return []

        all_links = set()
        self.logger.info(f"📌 Starting link extraction. Total pages: {len(self.pages)}")

        for page in self.pages:
            full_url = page
            self.logger.info(f"➡️ FROM HOME_PAGE.PY Navigating to: {full_url}")

            self.go_to_page(full_url)
            time.sleep(2)

            if "login" in self.browser.current_url:
                self.logger.warning(
                    f"🚨 Session lost! Redirected to login before accessing {full_url}. Logging in again...")
                browser, wait = login_fixture
                self.logger.info("Re-login successful.")
                self.go_to_page(full_url)

            current_url = self.browser.current_url
            self.logger.info(f"Arrived at: {current_url}")

            links = self.get_all_links()
            self.logger.info(f"🔗 Found {len(links)} links on {full_url}")
            all_links.update(links)

        self.logger.info(f"✅ Total unique links found: {len(all_links)}")
        return list(all_links)

    def is_logged_in(self):
        """Checks if the user is already logged in by verifying the current URL."""
        try:
            return "virtual-lab" in self.browser.current_url
        except AttributeError:
            self.logger.error("❌ Browser object is missing or invalid.")
            return False
        except TypeError:
            self.logger.error("❌ Unable to retrieve current URL.")
            return False
