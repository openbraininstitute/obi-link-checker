# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0


from selenium.webdriver.common.by import By


class LandingLocators:
    BANNER_TITLE = (By.XPATH, "//h1[contains(text(),'Create your Virtual Lab to build digital brain mod')]")
    BIG_IMG1 = (By.XPATH, "(//div[starts-with(@class,'SanityContentPreview_vignette')])[1]")
    BIG_IMG2 = (By.XPATH, "(//div[starts-with(@class,'SanityContentPreview_vignette')])[2]")
    BIG_IMG3 = (By.XPATH, "(//div[starts-with(@class,'SanityContentPreview_vignette')])[3]")
    GOTO_LAB = (By.XPATH, "//*[contains(@class, 'Menu_loginButton__')]")