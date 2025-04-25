# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

from selenium.common import TimeoutException

from locators.landing_locators import LandingLocators
from pages.home_page import HomePage


class LandingPage(HomePage):
    def __init__(self, browser, wait, base_url, lab_url, logger):
        super().__init__(browser, wait, base_url, logger)
        self.home_page = HomePage(browser, wait, base_url, logger)
        self.logger = logger
        self.base_url = base_url

    def go_to_landing_page(self, retries=3, delay=5):
        """Navigates to the OBI landing page and ensures it loads properly."""
        for attempt in range(retries):
            try:
                self.browser.set_page_load_timeout(60)
                self.browser.get(self.base_url)
                self.wait_for_page_ready(timeout=60)
                self.logger.info("✅ Landing Page loaded successfully.")
                return
            except TimeoutException:
                self.logger.warning(
                    f"⚠️ Landing Page load attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                self.wait.sleep(delay)
        raise TimeoutException("❌ Failed to load Landing Page after multiple attempts.")

    def click_go_to_lab(self):
        try:
            go_to_lab = self.find_element(LandingLocators.GOTO_LAB)
            go_to_lab.click()
            self.logger.info("✅ Clicked 'Go to Lab' button.")
        except Exception as e:
            self.logger.error(f"❌ Failed to click 'Go to Lab' button: {e}")
            raise
