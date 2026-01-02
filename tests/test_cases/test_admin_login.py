#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  test_admin_login.py
@Time    :  2025/12/30 18:38:36
@Author  :  owl
@Desp    : 管理员登录测试用例
"""

import allure
import pytest

from configs import config
from src.pages.admin_login_page import AdminLoginPage


@allure.feature("管理员登录")
@pytest.mark.video
class TestAdminLogin:
    """管理员登录"""

    # 设置参数
    @pytest.fixture(scope="class", autouse=True)
    def admin_login_data(self):
        """管理员登录数据准备"""
        # 这里可以添加数据准备逻辑，比如从配置文件或数据库获取管理员账号信息
        return config.users.admin

    @allure.title("管理员成功登录测试")
    @allure.description("测试管理员使用正确的用户名和密码登录系统")
    # @pytest.mark.video
    def test_admin_login_success(
        self,
        # video_recorder,
        driver,
        admin_login_data,
    ):
        admin_login_page = AdminLoginPage(driver)

        with allure.step("打开管理员登录页面"):
            admin_login_page.open()

        with allure.step("输入用户名"):
            admin_login_page.input_username(admin_login_data.username)

        with allure.step("输入密码"):
            admin_login_page.input_pwd(admin_login_data.password)

        with allure.step("识别并输入验证码"):
            admin_login_page.input_captcha()

        with allure.step("点击登录按钮"):
            admin_login_page.click_admin_login_btn()

        with allure.step("验证登录成功"):
            # 这里可以添加断言，验证登录是否成功
            assert admin_login_page.wait_for_title_contains(title_part="JPress后台"), (
                "登录失败，未跳转到JPress后台页面"
            )


if __name__ == "__main__":
    pytest.main(["-sv", __file__])
# end main
