import pytest
import requests
import logging
import time
import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pages.home_page import HomePage


def get_parent_element_text(soup, broken_link):
    """Finds the parent element of a broken link and extracts meaningful text."""
    element = soup.find("a", href=broken_link)

    if element:
        parent = element.find_parent(["tr", "td", "div", "span", "li"])  # Find relevant parent
        element_text = parent.get_text(strip=True) if parent else "[No text]"
        return f"Found in: {parent.name if parent else '[Unknown Element]'} - {element_text}"

    return "Found in: [Unknown Element] - [No text]"

@pytest.mark.usefixtures("setup", "login", "logger")
class TestLinks:
    def test_broken_links(self, setup, logger):
        """Logs in, scrapes all pages, and checks for broken links"""
        logging.info("🚀 Starting test: Checking for broken links.")

        browser, wait, base_url = setup
        home_page = HomePage(browser, wait, base_url, logger)
        dynamic_pages = home_page.pages
        all_links = set()
        soup = None

        link_sources = {}

        for page in dynamic_pages:
            print(f"\n🌍 Testing page: {page}")
            logging.info(f"🌍 Testing page: {page}")
            browser.get(page)
            time.sleep(2)  # Allow time for page load

            soup = BeautifulSoup(browser.page_source, "html.parser")
            page_links = home_page.get_all_links()

            for link in page_links:
                full_link = urljoin(base_url, link)
                link_sources[full_link] = page
            all_links.update(page_links)

        assert all_links, "❌ No links found on the website."
        print(f"🔗 FROM TESTLINKS***** Found {len(all_links)} links")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        broken_count = 0
        valid_count = 0

        with open("broken_links.log", "w", encoding="utf-8") as broken_links_log, \
             open("working_links.log", "w", encoding="utf-8") as working_links_log:

            for link in all_links:
                full_link = urljoin(base_url, link)
                source_page = link_sources.get(full_link, "[Unknown Page]")
                logging.info(f"➡️ Checking link: {full_link} (Found on: {source_page})")

                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(full_link, headers=headers, allow_redirects=True, timeout=5)
                    status = response.status_code

                    # Extract element text safely
                    found_element = soup.find(href=link)
                    element_text = "[Unknown Element] - [No text]"

                    if found_element:
                        # 🔥 FIXED: Ensuring correct parent element selection
                        parent_element = found_element.find_parent(lambda tag: tag.has_attr("class") and
                                                                               any(cls.startswith("ant-table-row") for
                                                                                   cls in tag["class"]))

                        if not parent_element:
                            # 🔥 FIXED: Try other meaningful tags as fallback
                            significant_tags = ["tr", "li", "div", "section", "article", "td", "ul", "ol"]
                            for tag in significant_tags:
                                parent_element = found_element.find_parent(tag)
                                if parent_element:
                                    break

                        if parent_element:
                            element_text = f"<{parent_element.name} class='{parent_element.get('class')}'> - {parent_element.get_text(strip=True)}"

                    if status >= 400:
                        logging.warning(
                            f"⚠️ Broken Link: {full_link} → Status {status} | Found in: {element_text} | Page: {source_page}")
                        broken_links_log.write(
                            f"{timestamp} | {full_link} → Status {status} | Found in: {element_text} | Page: {source_page}\n")
                        print(f"❌ Broken link detected: {full_link} | Page: {source_page} | Element: {element_text}")
                        broken_count += 1
                    else:
                        logging.info(f"✅ Working Link: {full_link} → Status {status}")
                        working_links_log.write(f"{timestamp} | {full_link} → Status {status}\n")
                        print(f"✅ Valid link detected: {full_link}")
                        valid_count += 1


                except requests.RequestException as e:
                    logging.error(f"❌ Broken Link: {full_link} (Error: {str(e)}) | Page: {source_page}")
                    broken_links_log.write(f"{timestamp} | {full_link} → ERROR: {str(e)} | Page: {source_page}\n")
                    print(
                        f"❌ Exception caught for: {full_link} - {str(e)} | Page: {source_page}")  # 🔥 FIXED: Now prints page
                    broken_count += 1

        # Print Summary:
        print("\n📊 Test Summary:")
        print(f"🔗 Total links found: {len(all_links)}")
        print(f"✅ Valid links: {valid_count}")
        print(f"❌ Broken links: {broken_count}")

        logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")