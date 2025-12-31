#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  webdriver_manager.py
@Time    :  2025/12/30 13:48:01
@Author  :  owl
@Desp    :  驱动管理
"""

import threading
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

from configs import config
from configs.path import BASE_DIR, DRIVERS_DIR

from .logger import logger


class DriverManager:
    """浏览器驱动管理器"""

    # 线程局部存储，每个线程独立驱动实例
    _local = threading.local()
    _current_config = config

    @classmethod
    def get_driver(cls, browser_type=None):
        """获取浏览器驱动"""
        if not hasattr(cls._local, "driver"):
            cls._local.driver = cls._create_driver(browser_type)
        return cls._local.driver

    @classmethod
    def _create_driver(cls, browser_type=None):
        """创建浏览器驱动"""
        # 从配置获取浏览器类型
        if browser_type is None:
            browser_type = cls._current_config.get("browser", "chrome")

        browser_type = browser_type

        logger.info(f"启动浏览器: {browser_type}")

        if browser_type == "chrome":
            return cls._create_chrome_driver()
        elif browser_type == "firefox":
            return cls._create_firefox_driver()
        elif browser_type == "edge":
            return cls._create_edge_driver()
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

    @classmethod
    def _create_chrome_driver(cls):
        """创建Chrome驱动"""
        logger.debug("创建Chrome浏览器驱动")

        options = webdriver.ChromeOptions()

        # 基础配置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # 无头模式
        headless = cls._current_config.get("headless", False)
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")

        # 禁用自动化提示
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 设置下载路径
        download_dir = BASE_DIR / "downloads"
        download_dir.mkdir(exist_ok=True)

        prefs = {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)

        # 自动下载和管理驱动
        # 避免并发下载ChromeDriver冲突
        try:
            # selenium4自动下载驱动
            driver = webdriver.Chrome(options=options)
        except Exception:
            logger.warning(
                f"使用webdriver-manager安装失败: {traceback.format_exc()}, 尝试使用系统驱动"
            )
            logger.info("使用本地ChromeDriver驱动")
            driver_path: Path = DRIVERS_DIR / "chromedriver.exe"
            logger.info(f"本地ChromeDriver路径: {driver_path}")  # 打印驱动路径
            service = ChromeService(str(driver_path))
            driver = webdriver.Chrome(service=service, options=options)
        # 绕过webdriver检测，防止被网站识别
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # 设置隐式等待
        timeout = cls._current_config.timeout
        driver.implicitly_wait(timeout)

        logger.info(
            f"Chrome浏览器启动成功，隐式等待: {timeout}秒，无头模式: {headless}"
        )
        return driver

    @classmethod
    def _create_firefox_driver(cls):
        """创建Firefox驱动"""
        logger.debug("创建Firefox浏览器驱动")

        options = webdriver.FirefoxOptions()

        headless = cls._current_config.get("headless", False)

        if headless:
            options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        timeout = cls._current_config.timeout
        driver.implicitly_wait(timeout)

        logger.info(f"Firefox浏览器启动成功，隐式等待: {timeout}秒")
        return driver

    @classmethod
    def _create_edge_driver(cls):
        """创建Edge驱动"""
        logger.debug("创建Edge浏览器驱动")

        options = webdriver.EdgeOptions()

        headless = cls._current_config.get("headless", False)

        if headless:
            options.add_argument("--headless")

        driver = webdriver.Edge(options=options)

        timeout = cls._current_config.timeout
        driver.implicitly_wait(timeout)

        logger.info(f"Edge浏览器启动成功，隐式等待: {timeout}秒")
        return driver

    @classmethod
    def quit_driver(cls):
        """退出浏览器驱动"""
        if hasattr(cls._local, "driver"):
            try:
                logger.info("关闭浏览器")
                cls._local.driver.quit()
            except Exception as e:
                logger.error(f"关闭浏览器时发生错误: {e}")
            finally:
                del cls._local.driver

    @classmethod
    def get_current_driver(cls):
        """获取当前驱动实例"""
        if hasattr(cls._local, "driver"):
            return cls._local.driver
        return None

    @classmethod
    def get_browser_name(cls):
        """获取当前浏览器名称"""
        driver = cls.get_current_driver()
        if driver:
            return driver.name
        return None

    @classmethod
    def take_screenshot(cls, name=None):
        """截图"""
        driver = cls.get_current_driver()
        if driver:
            return driver.get_screenshot_as_png()
        return None

    @classmethod
    def switch_to_new_tab(cls):
        """切换到新标签页"""
        driver = cls.get_current_driver()
        if driver:
            window_handles = driver.window_handles
            if len(window_handles) > 1:
                driver.switch_to.window(window_handles[-1])
                logger.info(f"切换到新标签页，共 {len(window_handles)} 个标签页")

    @classmethod
    def close_tab_and_switch_back(cls):
        """关闭当前标签页并切换回上一个"""
        driver = cls.get_current_driver()
        if driver and len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logger.info("关闭标签页，切回主标签页")

    @classmethod
    def clear_cookies(cls):
        """清除cookies"""
        driver = cls.get_current_driver()
        if driver:
            driver.delete_all_cookies()
            logger.info("已清除所有cookies")

    @classmethod
    def execute_script(cls, script, *args):
        """执行JavaScript"""
        driver = cls.get_current_driver()
        if driver:
            return driver.execute_script(script, *args)
        return None
