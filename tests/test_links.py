import pytest
import requests
import logging
import time
import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

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
        soup = None

        for page in dynamic_pages:
            browser.get(page)
            time.sleep(2)  # Allow time for page load

            # Use BeautifulSoup for better parsing
            soup = BeautifulSoup(browser.page_source, "html.parser")
            page_links = {link.get("href") for link in soup.find_all("a", href=True)}

            page_links = home_page.get_all_links()
            all_links.update(page_links)

        assert all_links, "❌ No links found on the website."
        print(f"🔗 FROM TESTLINKS***** Found {len(all_links)} links")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        broken_count = 0
        valid_count = 0

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

                    # Extract element text safely
                    element_text = "[No text]"
                    if soup:
                        found_element = soup.find("a", href=link)
                        if found_element:
                            element_text = found_element.get_text(strip=True) or "[No text]"

                    print(f"Checking: {full_link} - Status: {status}")

                    if status >= 400:
                        logging.warning(f"⚠️ Broken Link: {full_link} → Status {status}")
                        broken_links_log.write(f"{timestamp} | {full_link} → Status {status} | Found in: {element_text}\n")
                        broken_count += 1
                        print(f"❌ Broken link detected: {full_link} - Found in: {element_text}")
                    else:
                        logging.info(f"✅ Working Link: {full_link} → Status {status}")
                        working_links_log.write(f"{timestamp} | {full_link} → Status {status}\n")
                        valid_count += 1
                        print(f"✅ Valid link detected: {full_link}")

                except requests.RequestException as e:
                    logging.error(f"❌ Broken Link: {full_link} (Error: {str(e)})")
                    broken_links_log.write(f"{timestamp} | {full_link} → ERROR: {str(e)}\n")
                    broken_count += 1
                    print(f"❌ Exception caught for: {full_link} - {str(e)}")

        # Print Summary:
        print("\n📊 Test Summary:")
        print(f"🔗 Total links found: {len(all_links)}")
        print(f"✅ Valid links: {valid_count}")
        print(f"❌ Broken links: {broken_count}")

        logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")