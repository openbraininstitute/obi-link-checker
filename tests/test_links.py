import pytest
import requests
import logging
import time
import datetime
from urllib.parse import urljoin
from pages.home_page import HomePage


@pytest.mark.usefixtures("setup", "login")
class TestLinks:
    def test_broken_links(self, setup):
        """Logs in, scrapes all pages, and checks for broken links"""
        logging.info("🚀 Starting test: Checking for broken links.")

        browser, wait, base_url = setup
        home_page = HomePage(browser, wait, base_url)
        dynamic_pages = home_page.pages
        all_links = set()

        for page in dynamic_pages:
            browser.get(page)
            time.sleep(2)  # Allow time for page load
            page_links = home_page.get_all_links()
            all_links.update(page_links)

        assert all_links, "❌ No links found on the website."
        print(f"🔗 FROM TESTLINKS***** Found {len(all_links)} links")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Open log files for storing results
        with open("broken_links.log", "w", encoding="utf-8") as broken_links_log, \
             open("working_links.log", "w", encoding="utf-8") as working_links_log:

            for link in all_links:
                full_link = urljoin(base_url, link)
                logging.info(f"➡️ Checking link: {full_link}")

                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(full_link, headers=headers, allow_redirects=True, timeout=5)
                    status = response.status_code

                    if status >= 400:
                        logging.warning(f"⚠️ Broken Link: {full_link} → Status {status}")
                        broken_links_log.write(f"{timestamp} | {full_link} → Status {status}\n")
                    else:
                        logging.info(f"✅ Working Link: {full_link} → Status {status}")
                        working_links_log.write(f"{timestamp} | {full_link} → Status {status}\n")

                except requests.RequestException as e:
                    logging.error(f"❌ Broken Link: {full_link} (Error: {str(e)})")
                    broken_links_log.write(f"{timestamp} | {full_link} → ERROR: {str(e)}\n")

        logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")