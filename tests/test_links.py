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
from tests.conftest import navigate_to_login

SIGNIFICANT_TAGS = ["tr", "td", "div", "span", "li", "section", "article", "ul", "ol"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

def get_element_context(soup, href):
    """Extracts the parent and text context of a link in a BeautifulSoup document."""
    if not soup:
        return "[Unknown Element] - [No text]"

    element = soup.find("a", href=href)
    if not element:
        return "[Unknown Element] - [No text]"

    parent = element.find_parent(lambda tag: tag.has_attr("class") and any(cls.startswith("ant-table-row") for cls in tag["class"]))
    if not parent:
        for tag_name in SIGNIFICANT_TAGS:
            parent = element.find_parent(tag_name)
            if parent:
                break

    if parent:
        return f"<{parent.name} class='{parent.get('class')}'> - {parent.get_text(strip=True)}"
    return "[Unknown Element] - [No text]"


@pytest.mark.usefixtures("setup", "logger", "login")
class TestLinks:

    def test_broken_links(self, setup, logger, login):
        """Logs in, scrapes all pages, and checks for broken links"""
        logging.info("🚀 Starting test: Checking for broken links.")
        browser, wait, base_url, lab_id, project_id = setup
        home_page = HomePage(browser, wait, base_url, logger)

        pages = home_page.get_pages(lab_id, project_id)
        logger.info(f"Page is loaded, {browser.current_url}")

        landing_pages = [page for page in pages if "/app/virtual-lab" not in page]
        platform_pages = [page for page in pages if "/app/virtual-lab" in page]
        all_links, link_sources = {}, {}

        for group, label in [(landing_pages, "LANDING"), (platform_pages, "AUTHENTICATED")]:
            self.collect_links_from_pages(group, label, browser, base_url, wait, home_page, all_links, link_sources)

        assert all_links, "❌ No links found on the website."
        print(f"🔗 Found {len(all_links)} unique links")

        self.validate_links(base_url, all_links, link_sources)

    def collect_links_from_pages(self, pages, context, browser, base_url, wait, home_page, all_links, link_sources):
        for page in pages:
            logging.info(f"{context} Testing page: {page}")
            browser.get(page)
            time.sleep(2)
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            soup = BeautifulSoup(browser.page_source, "html.parser")
            page_links = home_page.get_all_links()

            for link in page_links:
                full_link = urljoin(base_url, link)
                all_links[full_link] = soup
                link_sources[full_link] = page

    def validate_links(self, base_url, all_links, link_sources):
        session = requests.Session()
        HEADERS["Referer"] = base_url
        session.headers.update(HEADERS)

        broken_count = valid_count = 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("broken_links.log", "w", encoding="utf-8") as broken_log, \
                open("working_links.log", "w", encoding="utf-8") as working_log:

            for full_link, soup in all_links.items():
                if "@" in full_link:
                    logging.info(f"Skipping links with '@': {full_link}")
                    continue

                source_page = link_sources.get(full_link, "[Unknown Page]")
                status_code = self.get_status(session, full_link)
                context_text = get_element_context(soup, full_link)

                if status_code == 403:
                    self.log_result(broken_log, full_link, status_code, source_page, context_text, "⚠️ Forbidden")
                    broken_count += 1
                elif status_code >= 400:
                    self.log_result(broken_log, full_link, status_code, source_page, context_text, "❌ Broken")
                    broken_count += 1
                else:
                    self.log_result(working_log, full_link, status_code, source_page, None, "✅ Working")
                    valid_count += 1

        self.print_summary(len(all_links), valid_count, broken_count)

    def get_status(self, session, url):
        try:
            return session.get(url, allow_redirects=True, timeout=5).status_code
        except requests.RequestException as e:
            logging.error(f"❌ Request failed for {url}: {str(e)}")
            return 500

    def log_result(self, log_file, link, status, page, context=None, label=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{timestamp} | {link} → Status {status} | Page: {page}"
        if context:
            message += f" | Found in: {context}"
        print(f"{label} {message}")
        logging.info(message)
        log_file.write(message + "\n")

    def print_summary(self, total, valid, broken):
        print("\n📊 Test Summary:")
        print(f"🔗 Total links: {total}")
        print(f"✅ Valid: {valid}")
        print(f"❌ Broken: {broken}")
        logging.info("✅ Test completed. Check broken_links.log and working_links.log for details.")
