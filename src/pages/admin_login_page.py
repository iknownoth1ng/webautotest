#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  admin_login_page.py
@Time    :  2025/12/30 18:24:10
@Author  :  owl
@Desp    :
"""

from configs import config
from src.core.base_page import BasePage
from src.core.element_locator import name, xpath
from src.utils.captcha_utils import CaptchaRecognizer


class AdminLoginPage(BasePage):
    # 定位器常量
    username_input = name("user")
    password_input = name("pwd")
    captcha_input = name("captcha")  # 根据实际页面调整
    captcha_img = xpath("//img[@id='captcha-img']")
    # captcha_img = id("captcha-img")
    login_button = xpath("//button[@type='submit']")  # 根据实际页面调整

    def __init__(self, driver):
        super().__init__(driver)
        self.url = f"{config.base_url}/admin/login"
        self.captcha_tool = CaptchaRecognizer(use_ocr=True)  # 按需初始化

    def open(self):
        """跳转到管理员登录页"""
        self.logger.info(f"打开登录页面: {self.url}")
        self.driver.get(self.url)
        self.wait_for_page_load()

    def input_username(self, username: str):
        self.input_text(self.username_input, username)

    def input_pwd(self, pwd: str):
        self.input_text(self.password_input, pwd)

    def input_captcha(self):
        captcha_text = self.handle_text_captcha()
        if captcha_text:
            # 4. 填写到输入框
            self.input_text(self.captcha_input, captcha_text)
            return True
        return False

    def click_admin_login_btn(self):
        self.click(self.login_button)

    def handle_text_captcha(self):
        """处理字符验证码"""
        # 1. 定位验证码图片元素
        captcha_element = self.find_element(self.captcha_img)
        # 2. 获取图片字节
        img_bytes = self.get_element_bytes(captcha_element)
        # 3. 识别
        captcha_text = self.captcha_tool.recognize_text(img_bytes)
        return captcha_text
