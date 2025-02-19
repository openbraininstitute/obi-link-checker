from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def get_all_links(self):
        """Returns all links from the page"""
        return [a.get_attribute("href") for a in self.driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
