#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  conftest.py
@Time    :  2025/12/30 13:50:29
@Author  :  owl
@Desp    :
"""

import os

import pytest

from configs import config
from configs.path import REPORTS_DIR, SCREENSHOTS_DIR, VIDEOS_DIR
from src.core.logger import logger
from src.core.webdriver_manager import DriverManager
from src.utils.allure_utils import AllureUtils
from src.utils.browser_video_recorder import BrowserVideoRecorder
from src.utils.file_utils import ensure_empty_directory


@pytest.fixture(scope="session", autouse=True)
def setup_environment(request):
    """设置测试环境"""
    # 获取命令行参数
    env = request.config.getoption("--env")
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")

    # 设置环境变量
    os.environ["ENV"] = env
    config._update_current_config()  # 重新加载配置以使用新的环境变量

    # 设置配置覆盖
    if browser:
        config.webdriver.browser = browser
    if headless is not None:
        config.webdriver.headless = headless

    logger.info(f"获取{os.getenv('ENV')}环境配置：{config}")

    yield


@pytest.fixture(scope="class", autouse=True)
def driver(request):
    """提供浏览器驱动"""
    test_name = request.node.name
    driver = DriverManager.get_driver(test_name = test_name)
    yield driver
    DriverManager.quit_driver()


@pytest.fixture(scope="class")
def admin_login(driver):
    """提供已登录的管理员页面"""
    from src.pages.admin_login_page import AdminLoginPage

    admin_login_page = AdminLoginPage(driver)
    admin_login_page.open()
    admin_login_page.input_username(config.users.admin.username)
    admin_login_page.input_pwd(config.users.admin.password)
    admin_login_page.input_captcha()
    admin_login_page.click_admin_login_btn()

    # 验证登录成功
    assert admin_login_page.wait_for_title_contains(title_part="JPress后台"), (
        "登录失败，未跳转到JPress后台页面"
    )

    return admin_login_page


@pytest.fixture(scope="function")
def video_recorder(driver, request):
    """提供浏览器视频录制器"""
    # 获取测试名称作为视频文件名
    test_name = request.node.name
    logger.info(f"初始化视频录制器: {test_name}")
    try:
        recorder = BrowserVideoRecorder(driver, fps=10, video_name=test_name)
        logger.info(f"开始录制视频: {recorder.video_path}")
        recorder.start_recording()
        yield recorder
        logger.info("停止录制视频")
        recorder.stop_recording()
        # 附加视频到Allure报告
        if recorder.video_path.exists():
            logger.info(f"附加视频到报告: {recorder.video_path}")
            AllureUtils.attach_video(str(recorder.video_path), str(recorder.video_path))
        else:
            logger.warning(f"视频文件不存在: {recorder.video_path}")
    except Exception as e:
        logger.error(f"视频录制失败: {e}")
        import traceback

        logger.error(traceback.format_exc())
        yield None


def pytest_configure(config):
    """pytest配置"""
    # 确保报告目录存在且为空
    # ensure_empty_directory(LOGS_DIR)
    ensure_empty_directory(REPORTS_DIR / "allure-results")
    ensure_empty_directory(REPORTS_DIR / "allure-report")
    ensure_empty_directory(SCREENSHOTS_DIR)
    ensure_empty_directory(VIDEOS_DIR)


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--env", action="store", default="dev", help="测试环境: dev, test, prod"
    )
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="浏览器类型: chrome, firefox, edge",
    )
    parser.addoption(
        "--headless", action="store_true", default=None, help="是否使用无头模式"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()

    # 只在测试用例执行失败时执行
    if rep.when == "call" and rep.failed:
        # logger.error(f"测试 {item.name} 失败: {call.excinfo.value}")
        # 截图
        if "driver" in item.fixturenames:
            driver = item.funcargs["driver"]
            try:
                AllureUtils.attach_screenshot("failure_screenshot", driver)
            except Exception as e:
                logger.error(f"截图失败: {e}")

        # 记录失败信息
        AllureUtils.attach_text("failure_info", rep.longreprtext)
    """创建测试报告时调用"""
    if call.when == "call" and call.excinfo is not None:
        logger.error(f"测试 {item.name} 失败: {call.excinfo.value}")


# @pytest.fixture(scope="function")
# def video_recorder(request):
#     """为每个测试提供录屏功能"""
#     recorder = None

#     # 检查是否需要录屏（可通过命令行参数或标记控制）
#     if request.config.getoption("--record-video", default=True):
#         recorder = VideoRecorder()
#         recorder.start_recording()
#         logger.debug(f"为测试 '{request.node.name}' 初始化录屏器")

#     yield recorder  # 将录屏器实例提供给测试函数

#     # 测试结束后保存视频
#     if recorder:
#         test_name = request.node.name
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         video_dir = VIDEOS_DIR
#         video_dir.mkdir(parents=True, exist_ok=True)
#         video_path = video_dir / f"{test_name}_{timestamp}.webm"

#         saved_path = recorder.stop_recording(video_path)

#         # 如果视频保存成功，可附加到Allure报告
#         if saved_path and saved_path.exists():
#             # 这里可以调用Allure附件添加方法
#             AllureUtils.attach_video(str(video_path), str(saved_path))


# def pytest_exception_interact(node, call, report):
#     """当异常发生时调用"""
#     if call.excinfo:
#         logger.error(f"测试失败: {node.name, call.excinfo}")
