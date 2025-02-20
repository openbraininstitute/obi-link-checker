import os
import pytest
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC


from pages.login_page import LoginPage


def pytest_addoption(parser):
    """Allows running tests in headless mode with --headless flag."""
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")
    parser.addoption("--browser", action="store", default="chrome", help="Choose browser: chrome, firefox, safari")
    parser.addoption("--env", action="store", default="staging", help="Choose environment: staging, production")


@pytest.fixture(scope="class", autouse=True)
def setup(request, pytestconfig):
    """Fixture to set up the WebDriver."""
    browser_name = pytestconfig.getoption("--browser")
    headless = pytestconfig.getoption("--headless")
    environment = pytestconfig.getoption("--env")

    if environment == "staging":
        base_url = "https://staging.openbluebrain.com/app"
    elif environment == "production":
        base_url = "https://openbluebrain.com/app"
    else:
        raise ValueError(f"Invalid environment: {environment}. Choose 'staging' or 'production'.")

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

    driver.maximize_window()
    driver.delete_all_cookies()

    request.cls.browser = driver
    request.cls.wait = wait
    request.cls.base_url = base_url

    yield driver, wait, base_url

    driver.quit()


@pytest.fixture(scope="function")
def navigate_to_login(setup):
    """Fixture that navigates to the login page."""
    driver, wait, base_url = setup
    login_page = LoginPage(driver, wait, base_url)

    username = os.getenv("OBI_USERNAME")
    password = os.getenv("OBI_PASSWORD")

    if not username or not password:
        raise ValueError("Missing OBI_USERNAME or OBI_PASSWORD environment variables.")

    # Open login page
    login_page.navigate_to_homepage()
    driver.execute_script("window.stop();")
    print(f"Navigated to: {driver.current_url}")

    login_button = login_page.find_login_button()
    assert login_button.is_displayed(), "Login button not displayed."

    login_button.click()
    wait.until(EC.url_contains("auth"))

    return login_page


@pytest.fixture(scope="function")
def login(setup, navigate_to_login):
    """Fixture to log in and ensure authentication."""
    driver, wait, base_url = setup
    login_page = navigate_to_login

    username = os.getenv("OBI_USERNAME")
    password = os.getenv("OBI_PASSWORD")

    login_page.login(username, password)

    try:
        login_page.wait_for_login_complete(timeout=30)
    except TimeoutException:
        pytest.fail(f"Login failed, current URL: {driver.current_url}")

    assert "/app/virtual-lab" in driver.current_url, f"Login failed, current URL: {driver.current_url}"
    print("Login successful. Current URL:", driver.current_url)

    yield driver, wait

    driver.delete_all_cookies()