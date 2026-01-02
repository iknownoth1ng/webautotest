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
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from configs import config
from configs.path import BASE_DIR, DRIVERS_DIR

from .logger import logger


class DriverManager:
    """浏览器驱动管理器"""

    # 线程局部存储，每个线程独立驱动实例
    _local = threading.local()
    _current_config = config
    _test_name = None

    @classmethod
    def get_driver(cls, browser_type=None,test_name= None):
        """获取浏览器驱动"""
        cls._test_name = test_name
        if not hasattr(cls._local, "driver"):
            cls._local.driver = cls._create_driver(browser_type)
        return cls._local.driver

    @classmethod
    def _create_driver(cls, browser_type=None):
        """创建浏览器驱动"""
        # 从配置获取浏览器类型
        if browser_type is None:
            browser_type = cls._current_config.webdriver.browser

        # 检查是否启用分布式模式
        mode = cls._current_config.webdriver.mode
        if mode == "grid":
            logger.info("使用Selenium Grid分布式模式")
            return cls._create_remote_driver(browser_type)
        else:
            logger.info("使用本地浏览器模式")
            return cls._create_local_driver(browser_type)

    @classmethod
    def _create_local_driver(cls, browser_type=None):
        """创建本地浏览器驱动"""
        if browser_type is None:
            browser_type = cls._current_config.webdriver.browser

        logger.info(f"启动本地浏览器: {browser_type}")

        driver_creators = {
            "chrome": cls._create_chrome_driver,
            "firefox": cls._create_firefox_driver,
            "edge": cls._create_edge_driver,
        }

        creator = driver_creators.get(browser_type)
        if creator:
            return creator()
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

    @classmethod
    def _create_remote_driver(cls, browser_type=None):
        """创建远程浏览器驱动（Grid模式）"""
        if browser_type is None:
            browser_type = cls._current_config.webdriver.browser

        # 获取Grid Hub地址
        grid_url = cls._current_config.webdriver.grid_hub_url
        logger.info(f"连接到Selenium Grid: {grid_url}, 浏览器: {browser_type}")

        # 创建浏览器选项
        options = cls._create_browser_options(browser_type, is_remote=True)

        try:
            driver = webdriver.Remote(command_executor=grid_url, options=options)
        except Exception as e:
            logger.error(f"连接到Selenium Grid失败: {e}")
            raise

        # 设置通用配置
        cls._configure_driver(driver, browser_type, grid_url)
        return driver

    @classmethod
    def _create_browser_options(cls, browser_type, is_remote=False):
        """创建浏览器选项配置"""
        options_creators = {
            "chrome": cls._create_chrome_options,
            "firefox": cls._create_firefox_options,
            "edge": cls._create_edge_options,
        }

        creator = options_creators.get(browser_type)
        if not creator:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

        return creator(is_remote)

    @classmethod
    def _create_chrome_options(cls, is_remote=False):
        """创建Chrome选项"""
        options = ChromeOptions()

        # 基础配置
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        # 录屏文件名称命名
        options.set_capability('se:name', cls._test_name)
        # 禁用录屏
        # options.set_capability('se:recordVideo', False)

        # 无头模式
        headless = cls._current_config.webdriver.headless
        if headless:
            if is_remote:
                options.add_argument("--headless")
            else:
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

        return options

    @classmethod
    def _create_firefox_options(cls, is_remote=False):
        """创建Firefox选项"""
        options = FirefoxOptions()

        headless = cls._current_config.webdriver.headless
        if headless:
            options.add_argument("--headless")

        return options

    @classmethod
    def _create_edge_options(cls, is_remote=False):
        """创建Edge选项"""
        options = EdgeOptions()

        headless = cls._current_config.webdriver.headless
        if headless:
            options.add_argument("--headless")

        return options

    @classmethod
    def _configure_driver(cls, driver, browser_type, grid_url=None):
        """配置驱动的通用设置"""
        # 设置隐式等待
        timeout = cls._current_config.webdriver.timeout
        driver.implicitly_wait(timeout)

        # 记录启动信息
        grid_info = f"，Grid: {grid_url}" if grid_url else ""
        logger.info(f"{browser_type}浏览器启动成功，隐式等待: {timeout}秒{grid_info}")

        # Chrome特殊处理
        if browser_type == "chrome" and not grid_url:
            # 绕过webdriver检测
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

    @classmethod
    def _create_chrome_driver(cls):
        """创建Chrome驱动"""
        logger.debug("创建Chrome浏览器驱动")

        options = cls._create_browser_options("chrome", is_remote=False)

        try:
            # selenium4自动下载驱动
            driver = webdriver.Chrome(options=options)
        except Exception:
            logger.warning(
                f"使用webdriver-manager安装失败: {traceback.format_exc()}, 尝试使用系统驱动"
            )
            logger.info("使用本地ChromeDriver驱动")
            driver_path: Path = DRIVERS_DIR / "chromedriver.exe"
            logger.info(f"本地ChromeDriver路径: {driver_path}")
            service = ChromeService(str(driver_path))
            driver = webdriver.Chrome(service=service, options=options)

        cls._configure_driver(driver, "chrome")
        return driver

    @classmethod
    def _create_firefox_driver(cls):
        """创建Firefox驱动"""
        logger.debug("创建Firefox浏览器驱动")

        options = cls._create_browser_options("firefox", is_remote=False)
        driver = webdriver.Firefox(options=options)

        cls._configure_driver(driver, "firefox")
        return driver

    @classmethod
    def _create_edge_driver(cls):
        """创建Edge驱动"""
        logger.debug("创建Edge浏览器驱动")

        options = cls._create_browser_options("edge", is_remote=False)
        driver = webdriver.Edge(options=options)

        cls._configure_driver(driver, "edge")
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
