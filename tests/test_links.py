import pytest
import logging
import requests
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.usefixtures("setup", "login")
class TestLinks:
    def test_broken_links(self, setup):
        """Logs in, scrapes all pages, and checks for broken links"""
        logging.info("🚀 Starting test: Checking for broken links.")
        print("🚀 Starting test: Checking for broken links.")

        browser, wait, base_url = setup

        login_page = LoginPage(browser, wait, base_url)
        login_page.navigate_to_homepage()
        print(f"🚀 Opened login page. Current URL: {browser.current_url}")

        if "error" in browser.current_url:
            pytest.fail(f"Login failed. Redirected to: {browser.current_url}")

        home_page = HomePage(browser, wait, base_url)
        all_links = home_page.login_and_scrape()

        assert all_links, "❌ No links found on the website."

        # Validate each link
        for link in all_links:
            logging.info(f"➡️ Checking link: {link}")
            print(f"➡️ Checking link: {link}")

            try:
                response = requests.head(link, allow_redirects=True, timeout=5)
                logging.info(f"✅ {link} → Status {response.status_code}")
                print(f"✅ {link} → Status {response.status_code}")

                if response.status_code >= 400:
                    logging.warning(f"⚠️ Potential issue: {link} returned {response.status_code}")
                    print(f"⚠️ Potential issue: {link} returned {response.status_code}")

            except requests.RequestException as e:
                logging.error(f"❌ Broken Link: {link} (Error: {str(e)})")
                print(f"❌ Broken Link: {link} (Error: {str(e)})")

        logging.info("✅ Test completed. Check broken_links.log for details.")
        print("✅ Test completed. Check broken_links.log for details.")

