# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


from pages.login_page import LoginPage
from util.util_base import load_config


def pytest_addoption(parser):
    """Allows running tests in headless mode with --headless flag."""
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")
    parser.addoption("--browser", action="store", default="chrome", help="Choose browser: chrome, firefox, safari")
    parser.addoption("--env", action="store", default="staging", help="Choose environment: staging, production")
    parser.addoption("--env_url", action="store", help="Base URL of the environment")


@pytest.fixture(scope="class", autouse=True)
def setup(request, pytestconfig):
    """Fixture to set up the WebDriver."""
    browser_name = pytestconfig.getoption("--browser")
    headless = pytestconfig.getoption("--headless")
    environment = pytestconfig.getoption("--env")
    base_url = pytestconfig.getoption("--env_url")

    if environment == "staging":
        base_url = "https://staging.openbraininstitute.org/app/virtual-lab"
    elif environment == "production":
        base_url = "https://openbraininstitute.org/app/virtual-lab"
    else:
        raise ValueError(f"Invalid environment: {environment}. Choose 'staging' or 'production'.")

    request.cls.base_url = base_url

    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif browser_name == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    elif browser_name == "safari":
        if headless:
            raise ValueError("Safari does not support headless mode.")
        options = SafariOptions()
        driver = webdriver.Safari(service=SafariService(), options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    driver.set_page_load_timeout(60)
    wait = WebDriverWait(driver, 20)

    # driver.maximize_window()
    driver.delete_all_cookies()

    request.cls.browser = driver
    request.cls.wait = wait
    request.cls.base_url = base_url

    yield driver, wait, base_url

    driver.quit()


@pytest.fixture(scope="function")
def navigate_to_login(setup, logger):
    """Fixture that navigates to the login page"""
    browser, wait, base_url = setup
    login_page = LoginPage(browser, wait, base_url, logger)
    print(f"INFO: Running withing conftest.py {login_page}")
    target_url = login_page.navigate_to_homepage()
    print(f"INFO: from contest.py Navigated to: {target_url}")
    login_page.wait_for_condition(
        lambda driver: "openid-connect" in driver.current_url,
        timeout=30,
        message="Timed out waiting for OpenID login page."
    )
    assert "openid-connect" in browser.current_url, f"Did not reach OpenID login page. Current URL: {browser.current_url}"

    print("DEBUG: Returning login_page from navigate_to_login")
    return login_page


@pytest.fixture(scope="function")
def login(setup, navigate_to_login, logger):
    """Fixture to log in and ensure user is authenticated."""
    browser, wait, base_url = setup
    login_page = navigate_to_login

    config = load_config()
    if not config:
        raise ValueError("Failed to load configuration")
    username = config.get('username')
    password = config.get('password')

    if not username or not password:
        raise ValueError("Username or password is missing in the configuration!")

    login_page.perform_login(username, password)
    login_page.wait_for_login_complete()
    print("Login successful. Current URL:", browser.current_url)
    yield browser, wait
    login_page.browser.delete_all_cookies()

@pytest.fixture(scope="class")
def logger():
    """Fixture to initialize the logger object"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set logging level

    project_root = os.path.abspath(os.path.dirname(__file__))
    allure_reports_dir = os.path.join(project_root, "allure_reports")
    log_file_path = os.path.join(allure_reports_dir, "report.log")

    # Ensure the logging directory exists
    os.makedirs(allure_reports_dir, exist_ok=True)

    # Remove existing handlers to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(filename=log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console (stream) handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_formatter = logging.Formatter("\n%(levelname)s : %(asctime)s : %(message)s")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    logger.info("🟢 Test started")
    yield logger  # Yield logger for use in tests

    logger.info("🛑 Test finished")