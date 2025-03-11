# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

from selenium.webdriver.common.by import By


class LoginPageLocators:
    FORM_CONTAINER = (By.CSS_SELECTOR, "div.form-container.display-none")
    LOGIN_FORM = (By.XPATH, "//form[@class='login-form']")
    LOGIN_BUTTON = (By.XPATH, "//a[contains(.,'Log in')]")
    LOGOUT = (By.XPATH, "//button[@type='button' and text()='Log out']")
    SIGN_IN = (By.XPATH, "//input[@type='submit']")
    USERNAME_FIELD = (By.XPATH, "//fieldset[@class='login-form-group']/input[@id='username']")
    PASSWORD_FIELD = (By.XPATH, "//fieldset[@class='login-form-group']/input[@id='password']")
    SUBMIT = (By.CSS_SELECTOR, ".login-form-submit")
    SUBMIT_BUTTON = (By.XPATH, "//input[@name='login']")