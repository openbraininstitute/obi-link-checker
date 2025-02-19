from .base_page import BasePage

class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://openbraininstitute.org"

    def open(self):
        """Opens the home page"""
        self.driver.get(self.url)