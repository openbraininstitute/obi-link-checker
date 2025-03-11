import time

from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from locators.login_locators import LoginPageLocators
from pages.base_page import CustomBasePage

class LoginPage(CustomBasePage):
    def __init__(self, browser, wait, base_url, logger):
        super().__init__(browser, wait, base_url)
        self.logger = logger

    def navigate_to_homepage(self):
        self.browser.delete_all_cookies()
        print(self.base_url, "PRINTING BASE_URL FROM login_page")
        target_url = self.base_url
        self.browser.get(target_url)
        print(f"______login page_______  {target_url}")
        WebDriverWait(self.browser, 30).until(
            lambda d: "openid-connect" in d.current_url or "auth" in d.current_url
        )
        # self.logger.info(f"INFO: target_url from pages/login_page.py:, {target_url}")
        # self.logger.info(f"INFO: Starting URL from pages/login_page.py:, {self.browser.current_url}")
        return target_url

    def find_login_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.LOGIN_BUTTON))

    def wait_for_login_complete(self, timeout=30):
        """Wait for login completion by checking a URL or element."""
        try:
            self.wait.until(EC.url_contains('app/virtual-lab'), timeout)
        except TimeoutException:
            print(
                f"Timeout waiting for URL to contain 'virtual-lab'. Current URL: "
                f"{self.browser.current_url}")
            raise

    def find_form_container(self):
        return self.find_element(LoginPageLocators.FORM_CONTAINER)

    def find_username_field(self):
        return self.find_element(LoginPageLocators.USERNAME_FIELD)

    def find_password_field(self):
        return self.wait.until(EC.presence_of_element_located(LoginPageLocators.PASSWORD_FIELD))

    def find_signin_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SIGN_IN))

    def find_logout_button(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.LOGOUT))

    def find_submit(self):
        return self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SUBMIT))

    def submit_button(self):
        return self.element_to_be_clickable(LoginPageLocators.SUBMIT_BUTTON)

    def perform_login(self, username, password):
        self.logger.info("Performing login with the provided credentials.")

        self.make_form_visible()
        username_field = self.find_username_field()
        print(f"DEBUG: Username field visible? {username_field.is_displayed()}")
        password_field = self.find_password_field()

        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        print("DEBUG: Submitted login credentials")

        try:
            self.wait_for_login_complete()
            self.wait.until(EC.url_contains("app/virtual-lab"))
            print("DEBUG: Login should be complete now.")
        except Exception as e:
            print(f"ERROR: Login process did not complete as expected: {e}")
        self.wait.until(EC.url_contains("app/virtual-lab"))

    def make_form_visible(self):
        """Use JavaScript to make the hidden form visible by removing 'display:none'."""
        form_container = self.find_form_container()
        self.browser.execute_script("arguments[0].style.display = 'block';", form_container)
        print("Form container made visible via JavaScript.")

    def ensure_element_interactable(self, element):
        """Ensure the element is visible and interactable, even if hidden."""
        if not element.is_displayed():
            self.browser.execute_script("arguments[0].style.display = 'block';", element)
        if not element.is_enabled():
            raise Exception(f"Element {element} is not enabled for interaction.")