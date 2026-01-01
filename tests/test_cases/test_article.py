#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  test_article.py
@Time    :  2021/12/29 20:42:17
@Author  :  owl
@Desp    : 文章管理测试用例
"""

import allure
import pytest
from selenium.webdriver.common.by import By

from src.pages.article_page import ArticlePage


@allure.feature("文章管理")
class TestArticle:
    """文章管理测试"""

    article_data = [
        ("我的文章1", "我的文章内容1", "文章保存成功。"),
        # ('我的文章2', '我的文章内容2', '文章保存成功。')
    ]

    @allure.title("添加文章成功测试")
    @allure.description("测试管理员成功添加新文章")
    @pytest.mark.parametrize("title, content, expected", article_data)
    def test_add_ok(self, admin_login, title, content, expected):
        """测试添加文章成功"""
        article_page = ArticlePage(admin_login.driver)

        with allure.step("点击文章管理菜单"):
            article_page.click_article()

        with allure.step("点击文章管理"):
            article_page.click_article_manage()

        with allure.step("点击添加文章按钮"):
            article_page.click_add_article()

        with allure.step(f"输入文章标题: {title}"):
            article_page.input_article_title(title)

        with allure.step(f"输入文章内容: {content}"):
            article_page.input_body(content)

        with allure.step("点击添加按钮"):
            article_page.click_add_btn()

        with allure.step("验证添加结果"):
            loc = (By.CLASS_NAME, "toast-message")
            msg = article_page.find_element(loc).text
            assert msg == expected


if __name__ == "__main__":
    pytest.main(["-sv", __file__])
