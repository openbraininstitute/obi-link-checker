
import time
import logging
from pages.base_page import CustomBasePage
from pages.login_page import LoginPage
from pages.urls import get_dynamic_pages


class HomePage(CustomBasePage):
    def __init__(self, browser, wait, base_url, logger):
        super().__init__(browser, wait, base_url, logger)
        self.logger = logging.getLogger(__name__)
        self.lab_id = "70de7008-d7d5-47f3-aa87-59ea47c19291"
        self.project_id = "7e37545c-ebc9-4ffa-b59c-7d3a211d8d01"
        self.pages = get_dynamic_pages(base_url,self.lab_id, self.project_id)
        self.logger = logger

    def go_to_home_page(self):
        """Navigates to the homepage."""
        self.go_to_page("")
        self.logger.info("🏠 Navigated to homepage.")

    def login_and_scrape(self):
        """Logs in before scraping all pages."""
        self.logger.info("🔄 Logging in before scraping...")

        if not self.is_logged_in():
            login_page = LoginPage(self.browser, self.wait, self.base_url)
            login_page.navigate_to_homepage()
            login_page.login()

            if "login" in self.browser.current_url:
                self.logger.error("❌ Login failed: Still on login page!")
                raise Exception("Login failed!")

            if self.browser.current_url == self.base_url:
                self.logger.warning("⚠️ Redirected back to base_url. Navigating to virtual lab manually.")
                self.browser.get(f"{self.base_url}")
                time.sleep(3)

            self.logger.info("✅ Login successful, ready to scrape.")
        else:
            self.logger.info("🔄 Already logged in, proceeding with scraping.")
        return self.get_all_links_from_all_pages()

    def get_all_links_from_all_pages(self):
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
                time.sleep(2)
                if "login" in self.browser.current_url:
                    self.logger.warning(
                    f"🚨 Session lost! Redirected to login before accessing {full_url}. Logging in again...")
                    login_page = LoginPage(self.browser, self.wait, self.base_url)
                    login_page.navigate_to_homepage()
                    login_page.login()

                if "login" in self.browser.current_url:
                    self.logger.error("❌ Re-login failed! Stopping execution.")
                    raise Exception("Login failure detected!")

                # ✅ Try navigating again after re-login
                self.go_to_page(full_url)
                time.sleep(2)

            current_url = self.browser.current_url
            self.logger.info(f"✅ Arrived at: {current_url}")

            links = self.get_all_links()
            self.logger.info(f"🔗 Found {len(links)} links on {full_url}")
            all_links.update(links)

        self.logger.info(f"✅ Total unique links found: {len(all_links)}")
        return list(all_links)

    def is_logged_in(self):
        """Checks if the user is already logged in by verifying the current URL."""
        try:
            return "virtual-lab" in self.browser.current_url  # Example check
        except AttributeError:  # If `self.browser` is None or doesn't have `current_url`
            self.logger.error("❌ Browser object is missing or invalid.")
            return False
        except TypeError:  # If `current_url` is None
            self.logger.error("❌ Unable to retrieve current URL.")
            return False
