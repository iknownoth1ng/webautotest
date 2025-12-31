#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  allure_utils.py
@Time    :  2025/12/30 19:10:08
@Author  :  owl
@Desp    :
"""

import allure


class AllureUtils:
    """Allure报告工具"""

    @staticmethod
    def attach_screenshot(name, driver):
        """附加截图到报告"""
        if driver:
            screenshot = driver.get_screenshot_as_png()
            allure.attach(
                screenshot, name=name, attachment_type=allure.attachment_type.PNG
            )

    @staticmethod
    def attach_img(name, image_bytes):
        """附加图片到报告"""
        allure.attach(
            image_bytes, name=name, attachment_type=allure.attachment_type.PNG
        )

    @staticmethod
    def attach_text(name, content):
        """附加文本到报告"""
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_html(name, html):
        """附加HTML到报告"""
        allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def attach_json(name, data):
        """附加JSON到报告"""
        import json

        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False),
            name=name,
            attachment_type=allure.attachment_type.JSON,
        )

    @staticmethod
    def attach_video(name, video_path):
        """附加视频到报告"""
        with open(video_path, "rb") as f:
            # video_content = f.read()
            allure.attach(
                f.read(), name=name, attachment_type=allure.attachment_type.MP4
            )
