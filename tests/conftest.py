# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC

from pages.landing_page import LandingPage
from pages.login_page import LoginPage


def pytest_addoption(parser):
    """Allows running tests in headless mode with --headless flag."""
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")
    parser.addoption("--browser-name", action="store", default="chrome", help="Choose browser: chrome, firefox, safari")
    parser.addoption("--env", action="store", default="staging", help="Choose environment: staging, production")
    parser.addoption("--env_url", action="store", help="Base URL of the environment")

@pytest.fixture(scope="session")
def test_config(pytestconfig):
    """Gets credentials and IDS returns the correct environment-specific settings."""
    username = os.getenv("OBI_USERNAME")
    password = os.getenv("OBI_PASSWORD")
    env = pytestconfig.getoption("env")

    if not username or not password:
        raise ValueError("Username or password is missing in the configuration!")

    if env =="staging":
        base_url = "https://staging.openbraininstitute.org"
        lab_url = f"{base_url}/app/virtual-lab"
        lab_id = os.getenv("LAB_ID_STAGING")
        project_id = os.getenv("PROJECT_ID_STAGING")
    elif env == "production":
        base_url = "https://www.openbraininstitute.org"
        lab_url = f"{base_url}/app/virtual-lab"
        lab_id = os.getenv("LAB_ID_PRODUCTION")
        project_id = os.getenv("PROJECT_ID_PRODUCTION")
    else:
        raise ValueError(f"Invalid environment: {env}")

    return {
        "username": username,
        "password": password,
        "base_url": base_url,
        "lab_url": lab_url,
        "lab_id": lab_id,
        "project_id": project_id,
    }

@pytest.fixture(scope="class", autouse=True)
def setup(request, pytestconfig, test_config):
    """Fixture to set up the WebDriver."""
    environment = pytestconfig.getoption("env")
    browser_name = pytestconfig.getoption("--browser-name")
    base_url = test_config["base_url"]
    lab_id = test_config["lab_id"]
    project_id = test_config["project_id"]

    print(f"Starting tests in {environment.upper()} mode.")

    if browser_name == "chrome":
        options = ChromeOptions()
        if pytestconfig.getoption("--headless"):
            options.add_argument("--headless")
            options.add_argument("--ignore-certificate-errors")
        browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        if pytestconfig.getoption("--headless"):
            options.add_argument("--headless")
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    browser.set_page_load_timeout(60)
    wait = WebDriverWait(browser, 20)

    request.cls.base_url = base_url
    request.cls.lab_id = lab_id
    request.cls.project_id = project_id

    request.cls.browser = browser
    request.cls.wait = wait

    yield browser, wait, base_url, lab_id, project_id

    if browser is not None:
        browser.quit()

@pytest.fixture(scope="function")
def navigate_to_landing_page(setup, logger, test_config):
    """Fixture to open and verify the OBI Landing Page before login."""
    browser, wait, base_url, lab_id, project_id = setup
    landing_page = LandingPage(browser, wait, test_config["base_url"], test_config["lab_url"], logger)
    landing_page.go_to_landing_page()

    yield landing_page

@pytest.fixture(scope="function")
def navigate_to_login(setup, navigate_to_landing_page, logger, request, test_config):
    """Fixture that navigates to the login page"""
    browser, wait, lab_url, lab_id, project_id = setup
    landing_page = navigate_to_landing_page
    landing_page.click_go_to_lab()

    WebDriverWait(browser, 60).until(
        EC.url_contains("openid-connect"),
        message="Timed out waiting for OpenID login page"
    )
    return LoginPage(browser, wait, test_config["lab_url"], logger)

@pytest.fixture(scope="function")
def login(setup, navigate_to_login, test_config, logger):
    """Fixture to log in and ensure user is authenticated."""
    browser, wait, lab_url, lab_id, project_id = setup
    login_page = navigate_to_login

    username = test_config.get("username")
    password = test_config.get("password")

    if not username or not password:
        raise ValueError("Username or password is missing in the configuration!")

    login_page.perform_login(username, password)
    login_page.wait_for_login_complete()
    print("Login successful. Current URL:", browser.current_url)
    login_page = LoginPage(browser, wait, lab_url, logger)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Pytest hook implementation to handle test reporting.

    - Captures screenshots when a test fails.
    - Embeds the screenshot into the HTML report.
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when in ("call", "setup"):
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            print("Test failed - capturing screenshot")

            project_root = os.path.abspath(os.path.dirname(__file__))
            screenshots_dir = os.path.join(project_root, "..", "screenshots", "errors")
            os.makedirs(screenshots_dir, exist_ok=True)

            test_name = report.nodeid.replace("::", "_").replace("/", "_")
            screenshot_path = os.path.join(screenshots_dir, f"{test_name}.png")
            print(f"Screenshot path: {screenshot_path}")

            browser = None
            if hasattr(item, "cls"):
                browser = getattr(item.cls, "browser", None)
            if not browser:
                browser = getattr(item, "_browser", None)
                print(f"Browser found in item attribute")

            if browser:
                try:
                    print("Browser object found - making screenshot")
                    _capture_screenshot(screenshot_path, browser)
                    if os.path.exists(screenshot_path):
                        print(f"Screenshot successfully saved at: {screenshot_path}")
                        html = (
                                f'<div><img src="{os.path.relpath(screenshot_path)}"'
                                f'alt="screenshot" style="width:304px;height:228px;"'
                                f'onclick="window.open(this.src)" '
                                'align="right"/></div>') % os.path.relpath(screenshot_path)
                        extra.append(pytest_html.extras.html(html))
                    else:
                        print(f"Screenshot not found at: {screenshot_path}")
                except Exception as e:
                    print(f"Exception occurred while capturing screenshot: {e}")
            else:
                print("No browser object found - skipping screenshot capture")

        report.extra = extra
def _capture_screenshot(name, browser):
    """
        Helper function to capture and save a screenshot.

        - Ensures the target directory exists.
        - Uses the browser object to capture a full-page screenshot.
        :param name: The full path where the screenshot will be saved.
        :param browser: The browser object used for screenshot capture.
        """
    try:
        print(f"Creating error  directory at:{os.path.dirname(name)}")
        os.makedirs(os.path.dirname(name), exist_ok=True)
        print(f"Saving screenshot to: {name}")
        browser.save_screenshot(name)
        print(f"Screenshot captured: {name}")
    except Exception as e:
        print(f"Failed to capture screenshot '{name}': {e}")

@pytest.fixture(scope="class")
def logger():
    """Fixture to initialize the logger object"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    project_root = os.path.abspath(os.path.dirname(__file__))
    logs_dir = os.path.join(project_root, "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)


    log_file_path = os.path.join(logs_dir, "error.log")

    # Remove existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(filename=log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_formatter = logging.Formatter("\n%(levelname)s : %(asctime)s : %(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    logger.info("🟢 Test started")
    yield logger

    logger.info("🛑 Test finished")