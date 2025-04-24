# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests
import logging
import time
import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from pages.home_page import HomePage


def get_parent_element_text(soup, broken_link):
    """Finds the parent element of a broken link and extracts meaningful text."""
    element = soup.find("a", href=broken_link)

    if element:
        parent = element.find_parent(["tr", "td", "div", "span", "li"])
        element_text = parent.get_text(strip=True) if parent else "[No text]"
        return f"Found in: {parent.name if parent else '[Unknown Element]'} - {element_text}"

    return "Found in: [Unknown Element] - [No text]"

@pytest.mark.usefixtures("setup", "login", "logger")
class TestLinks:
    def test_broken_links(self, setup, logger):
        """Logs in, scrapes all pages, and checks for broken links"""
        logging.info("🚀 Starting test: Checking for broken links.")

        browser, wait, base_url, lab_id, project_id = setup
        home_page = HomePage(browser, wait, base_url, logger)
        print(f"DEBUG: Using lab_id={lab_id}, project_id={project_id}")
        dynamic_pages = home_page.get_pages(lab_id, project_id)
        logger.info(f"Explore page is loaded, {browser.current_url}")
        all_links = set()
        soup = None
        link_sources = {}


        for page in dynamic_pages:
            print(f"\n🌍 Testing page: {page}")
            logging.info(f"🌍 Testing page: {page}")
            browser.get(page)
            time.sleep(2)  # Allow time for page load
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

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

            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            for link in all_links:
                full_link = urljoin(base_url, link)
                source_page = link_sources.get(full_link, "[Unknown Page]")
                logging.info(f"➡️ Checking link: {full_link} (Found on: {source_page})")

                try:
                    response = session.get(
                        full_link,
                        allow_redirects=True,
                        timeout=5,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                            "Referer": base_url,
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "en-US,en;q=0.9",
                            "Connection": "keep-alive",
                        },
                    )
                    status_code = response.status_code

                except requests.RequestException as e:
                    logging.error(f"❌ Request failed for {full_link}: {str(e)}")
                    status_code = 500

                if status_code is None:
                    status_code = 500

                found_element = soup.find(href=link)
                element_text = "[Unknown Element] - [No text]"

                if found_element:
                    parent_element = found_element.find_parent(lambda tag: tag.has_attr("class") and
                                                                           any(cls.startswith("ant-table-row") for
                                                                               cls in tag["class"]))

                    if not parent_element:
                        significant_tags = ["tr", "li", "div", "section", "article", "td", "ul", "ol"]
                        for tag in significant_tags:
                            parent_element = found_element.find_parent(tag)
                            if parent_element:
                                break

                    if parent_element:
                        element_text = f"<{parent_element.name} class='{parent_element.get('class')}'> - {parent_element.get_text(strip=True)}"

                if status_code == 403:
                    logging.warning(f"⚠️ Forbidden Link (403): {full_link} | Page: {source_page}")
                    broken_links_log.write(f"{timestamp} | {full_link} → Status 403 | Page: {source_page}\n")
                    print(f"⚠️ Forbidden link detected: {full_link} | Page: {source_page}")

                elif status_code >= 400:
                    logging.warning(
                        f"❌ Broken Link: {full_link} → Status {status_code} | Found in: {element_text} | Page: {source_page}")
                    broken_links_log.write(
                        f"{timestamp} | {full_link} → Status {status_code} | Found in: {element_text} | Page: {source_page}\n")
                    print(f"❌ Broken link detected: {full_link} | Page: {source_page} | Element: {element_text}")
                    broken_count += 1

                else:
                    logging.info(f"✅ Working Link: {full_link} | Page: {source_page}")
                    working_links_log.write(f"{timestamp} | {full_link} → Status {status_code} | Page: {source_page}\n")
                    print(f"✅ Valid link detected: {full_link} | Page: {source_page}")
                    valid_count += 1

        # Print Summary:
        print("\n📊 Test Summary:")
        print(f"🔗 Total links found: {len(all_links)}")
        print(f"✅ Valid links: {valid_count}")
        print(f"❌ Broken links: {broken_count}")

        logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")

