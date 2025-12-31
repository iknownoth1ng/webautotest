#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  captcha_utils.py
@Time    :  2025/12/31 12:07:52
@Author  :  owl
@Desp    :  验证码处理工具
"""

from pathlib import Path

import ddddocr
from selenium.webdriver.remote.webelement import WebElement

from src.core.logger import logger
from src.utils.allure_utils import AllureUtils


class CaptchaRecognizer:
    """验证码识别工具类"""

    def __init__(self, use_det=False, use_ocr=True):
        """
        初始化识别器
        :param use_det: 是否启用目标检测模型（用于点选验证码）
        :param use_ocr: 是否启用OCR模型（用于字符验证码）
        """
        self.ocr = None
        self.det = None
        # 按需初始化，避免不必要的资源加载
        if use_ocr:
            self.ocr = ddddocr.DdddOcr(show_ad=False)
            logger.debug("OCR模型加载完成")
        if use_det:
            self.det = ddddocr.DdddOcr(det=True, ocr=False, show_ad=False)
            logger.debug("目标检测模型加载完成")

    def recognize_text(self, image_bytes):
        """识别普通字符/数字验证码[citation:5][citation:8]"""
        if not self.ocr:
            raise ValueError("OCR模型未启用")
        try:
            result = self.ocr.classification(image_bytes)
            # 记录到Allure
            AllureUtils.attach_text(
                "Captcha OCR Result", f"验证码识别成功，结果: {result}"
            )
            AllureUtils.attach_img("原始验证码图", image_bytes)
            logger.info(f"字符验证码识别结果: {result}")
            return result
        except Exception as e:
            logger.error(f"字符验证码识别失败: {e}")
            return None

    def recognize_slide(self, target_bytes, background_bytes):
        """识别滑块验证码缺口位置[citation:1][citation:8]"""
        try:
            # 使用slide_match计算缺口位置
            slide_det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
            res = slide_det.slide_match(
                target_bytes, background_bytes, simple_target=True
            )
            logger.info(f"滑块缺口位置: {res}")
            # res 格式为 {'target': [x, y, width, height]}
            return res
        except Exception as e:
            logger.error(f"滑块验证码识别失败: {e}")
            return None

    def detect_objects(self, image_bytes):
        """检测点选验证码中的目标位置[citation:8]"""
        if not self.det:
            raise ValueError("目标检测模型未启用")
        try:
            bboxes = self.det.detection(image_bytes)
            logger.info(f"检测到 {len(bboxes)} 个目标")
            # bboxes 格式为 [[x1, y1, x2, y2], ...]
            return bboxes
        except Exception as e:
            logger.error(f"目标检测失败: {e}")
            return []

    # ---------- 针对Selenium的便捷方法 ----------
    def get_element_bytes(self, element: WebElement):
        """将WebElement截图转换为字节"""
        screenshot_bytes = element.screenshot_as_png
        return screenshot_bytes

    def get_page_screenshot_bytes(self, driver):
        """将整个页面截图转换为字节"""
        screenshot_path = Path("temp_screenshot.png")
        driver.save_screenshot(str(screenshot_path))
        with open(screenshot_path, "rb") as f:
            bytes_data = f.read()
        screenshot_path.unlink()  # 删除临时文件
        return bytes_data
