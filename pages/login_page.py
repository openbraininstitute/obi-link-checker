import os
import logging

import os
import logging
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class LoginPage(BasePage):
    FORM_CONTAINER = (By.CSS_SELECTOR, "div.form-container.display-none")
    LOGIN_FORM = (By.XPATH, "//form[@class='login-form']")
    LOGIN_BUTTON = (By.XPATH, "//a[contains(.,'Log in')]")
    LOGOUT = (By.XPATH, "//button[@type='button' and text()='Log out']")
    SIGN_IN = (By.XPATH, "//input[@type='submit']")
    USERNAME_FIELD = (By.XPATH, "//fieldset[@class='login-form-group']/input[@id='username']")
    PASSWORD_FIELD = (By.XPATH, "//fieldset[@class='login-form-group']/input[@id='password']")
    SUBMIT = (By.CSS_SELECTOR, ".login-form-submit")

    def __init__(self, browser, wait, base_url):
        super().__init__(browser, wait, base_url)
        self.logger = logging.getLogger(__name__)
        self.login_url = f"{self.base_url}/login"

    def navigate_to_homepage(self):
        self.browser.delete_all_cookies()
        target_url = self.base_url
        self.browser.get(target_url)
        print("Starting URL from pages/login_page.py:", self.browser.current_url)
        return self.browser.current_url

    def find_login_button(self):
        """Finds the login button."""
        return self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))

    def make_form_visible(self):
        """Use JavaScript to make the hidden login form visible."""
        form_container = self.wait.until(EC.presence_of_element_located(self.FORM_CONTAINER))
        self.browser.execute_script("arguments[0].style.display = 'block';", form_container)
        self.logger.info("✅ Made login form visible via JavaScript.")

    def login(self, username=None, password=None):
        """Logs in using provided credentials or environment variables."""
        self.logger.info("Starting login process.")

        username = username or os.getenv("OBI_USERNAME")
        password = password or os.getenv("OBI_PASSWORD")

        if not username or not password:
            self.logger.error("❌ Missing OBI_USERNAME or OBI_PASSWORD environment variables.")
            raise ValueError("Username or password is missing.")

        self.navigate_to_homepage()
        self.find_login_button().click()
        self.make_form_visible()

        self.wait.until(EC.presence_of_element_located(self.USERNAME_FIELD)).send_keys(username)
        self.wait.until(EC.presence_of_element_located(self.PASSWORD_FIELD)).send_keys(password + Keys.ENTER)

        self.wait_for_login_complete()

        if "login" in self.browser.current_url:
            raise AssertionError("❌ Login failed: Still on login page!")

        if self.browser.current_url == self.base_url:
            self.logger.warning("⚠️ Redirected back to base_url. Navigating to virtual lab manually.")
            self.browser.get(f"{self.base_url}/virtual-lab")

        self.logger.info("✅ Successfully logged in.")

    def wait_for_login_complete(self, timeout=30):
        """Waits until login is complete by checking the URL."""
        try:
            self.wait.until(EC.url_contains("app/virtual-lab"), timeout)
        except TimeoutException:
            print(f"Timeout waiting for login. Current URL: {self.browser.current_url}")
            raise

    def find_logout_button(self):
        """Finds the logout button after login."""
        return self.wait.until(EC.element_to_be_clickable(self.LOGOUT))
