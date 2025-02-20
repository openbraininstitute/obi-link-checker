import time

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
        home_page = HomePage(browser, wait, base_url)
        all_links = home_page.login_and_scrape()

        assert all_links, "❌ No links found on the website."

        broken_links_log = open("broken_links.log", "w", encoding="utf-8")
        working_links_log = open("working_links.log", "w", encoding="utf-8")

        try:
            for link in all_links:
                time.sleep(13)
                logging.info(f"➡️ Checking link: {link}")
                print(f"➡️ Checking link: {link}")

                try:
                    response = requests.head(link, allow_redirects=True, timeout=5)
                    logging.info(f"✅ {link} → Status {response.status_code}")
                    print(f"✅ {link} → Status {response.status_code}")

                    if response.status_code >= 400:
                        logging.warning(f"⚠️ Broken Link: {link} returned {response.status_code}")
                        print(f"⚠️ Broken Link: {link} returned {response.status_code}")
                        broken_links_log.write(f"{link} → Status {response.status_code}\n")
                    else:
                        working_links_log.write(f"{link} → Status {response.status_code}\n")

                except requests.RequestException as e:
                    logging.error(f"❌ Broken Link: {link} (Error: {str(e)})")
                    print(f"❌ Broken Link: {link} (Error: {str(e)})")
                    broken_links_log.write(f"{link} → ERROR: {str(e)}\n")

                    # ✅ Close log files
        finally:
                broken_links_log.close()
                working_links_log.close()

                logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")
                print("✅ Test completed. Check broken_links.log and working_links.log for details.")

