#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  base_page.py
@Time    :  2025/12/30 13:26:20
@Author  :  owl
@Desp    :
"""

import time
from pathlib import Path

from selenium.common import JavascriptException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from configs.path import SCREENSHOTS_DIR

from .logger import logger


class BasePage:
    """带日志记录的页面基类"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)
        self.logger = logger

    def find_element(self, locator):
        """查找元素"""
        try:
            self.logger.log_action("查找元素", locator)
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"成功找到元素: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"元素查找超时: {locator}")
            raise

    def find_elements(self, locator):
        """查找多个元素"""
        try:
            self.logger.log_action("查找多个元素", locator)
            elements = self.wait.until(EC.presence_of_all_elements_located(locator))
            self.logger.debug(f"找到 {len(elements)} 个元素: {locator}")
            return elements
        except TimeoutException:
            self.logger.error(f"元素查找超时: {locator}")
            raise

    def click(self, locator):
        """点击元素"""
        try:
            self.logger.log_action("点击", locator)
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
            self.logger.info(f"点击成功: {locator}")
        except TimeoutException:
            self.logger.error(f"元素不可点击或超时: {locator}")
            raise

    def input_text(self, locator, text):
        """输入文本"""
        try:
            self.logger.log_action("输入文本", locator, f"内容: {text}")
            element = self.find_element(locator)
            element.clear()
            element.send_keys(text)
            self.logger.debug(f"文本输入完成: {locator}")
        except Exception as e:
            self.logger.error(f"文本输入失败: {locator} - 错误: {str(e)}")
            raise

    def get_text(self, locator):
        """获取元素文本"""
        try:
            self.logger.log_action("获取文本", locator)
            element = self.find_element(locator)
            text = element.text
            self.logger.debug(f"获取到文本: {text}")
            return text
        except Exception as e:
            self.logger.error(f"获取文本失败: {locator} - 错误: {str(e)}")
            raise

    def is_displayed(self, locator):
        """检查元素是否可见"""
        try:
            self.logger.log_action("检查元素可见性", locator)
            element = self.find_element(locator)
            result = element.is_displayed()
            self.logger.debug(f"元素可见性: {locator} = {result}")
            return result
        except (TimeoutException, NoSuchElementException):
            self.logger.warning(f"元素不可见或不存在: {locator}")
            return False

    def wait_for_element(self, locator, timeout=10):
        """等待元素出现"""
        try:
            self.logger.log_action("等待元素", locator, f"超时: {timeout}s")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"元素等待成功: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"元素等待超时: {locator} - 超时设置: {timeout}s")
            raise

    # def scroll_to_element(self, locator):
    #     """滚动到元素"""
    #     try:
    #         self.logger.log_action("滚动到元素", locator)
    #         element = self.find_element(locator)
    #         self.driver.execute_script(
    #             "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
    #             element,
    #         )
    #         self.logger.debug(f"滚动到元素完成: {locator}")
    #     except Exception as e:
    #         self.logger.error(f"滚动到元素失败: {locator} - 错误: {str(e)}")
    #         raise

    def take_screenshot(self, name=None):
        """截图并记录日志"""
        try:
            if not name:
                name = f"screenshot_{self.__class__.__name__}"

            self.logger.log_action("截图", details=f"文件名: {name}")
            screenshot_dir = Path(SCREENSHOTS_DIR)
            screenshot_dir.mkdir(exist_ok=True)

            filepath = screenshot_dir / f"{name}.png"
            self.driver.save_screenshot(str(filepath))
            self.logger.debug(f"截图保存到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return None

    def navigate_to(self, url):
        """导航到URL"""
        self.logger.log_action("页面跳转", details=f"URL: {url}")
        self.driver.get(url)
        self.logger.info(f"已跳转到: {url}")

    def get_current_url(self):
        """获取当前URL"""
        url = self.driver.current_url
        self.logger.debug(f"当前URL: {url}")
        return url

    def refresh_page(self):
        """刷新页面"""
        self.logger.log_action("刷新页面")
        self.driver.refresh()
        self.logger.info("页面刷新完成")
        self.logger.info("页面刷新完成")

    def wait_for_page_load(self, timeout: int = 30):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.logger.info("页面加载完成")
        except TimeoutException:
            self.logger.warning("页面加载超时")

    def get_element_bytes(self, element: WebElement):
        """将WebElement截图转换为字节"""
        screenshot_bytes = element.screenshot_as_png
        return screenshot_bytes

    def wait_for_title_contains(self, title_part: str, timeout: int = 10):
        """等待页面标题包含指定文本"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.title_contains(title_part))

    def wait_for_title_is(self, expected_title: str, timeout: int = 10):
        """等待页面标题完全匹配"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.title_is(expected_title))

    # * 新增一些方法
    # ========== 1. 增强点击与截图 ==========
    def click_with_screenshot(self, locator, screenshot_name=None):
        """
        点击元素并自动截图（常用于关键步骤验证）
        :param locator: 元素定位器
        :param screenshot_name: 截图文件名（不包含路径和扩展名）
        :return: 点击的元素
        """
        try:
            self.logger.log_action("带截图点击", locator)
            element = self.wait.until(EC.element_to_be_clickable(locator))

            # 点击前截图
            if screenshot_name:
                self.take_screenshot(f"before_click_{screenshot_name}")

            element.click()
            self.logger.info(f"点击成功: {locator}")

            # 点击后截图
            if screenshot_name:
                self.take_screenshot(f"after_click_{screenshot_name}")

            return element

        except Exception as e:
            self.logger.error(f"带截图点击失败: {locator} - {e}")
            # 失败时截图
            self.take_screenshot(f"click_failed_{screenshot_name or 'unknown'}")
            raise

    # ========== 2. 高级键鼠操作 ==========
    def hover_and_click(self, hover_locator, click_locator):
        """悬停后点击（用于下拉菜单等）"""
        try:
            self.logger.log_action(
                "悬停并点击", hover_locator, f"然后点击: {click_locator}"
            )

            # 悬停到第一个元素
            hover_element = self.wait.until(
                EC.presence_of_element_located(hover_locator)
            )
            self.actions.move_to_element(hover_element).perform()
            self.logger.debug(f"悬停完成: {hover_locator}")
            time.sleep(0.5)  # 等待悬停效果

            # 点击第二个元素
            click_element = self.wait.until(EC.element_to_be_clickable(click_locator))
            click_element.click()
            self.logger.info("悬停点击完成")

        except Exception as e:
            self.logger.error(f"悬停点击失败: {e}")
            raise

    def double_click(self, locator):
        """双击元素"""
        try:
            self.logger.log_action("双击", locator)
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.actions.double_click(element).perform()
            self.logger.info(f"双击完成: {locator}")
        except Exception as e:
            self.logger.error(f"双击失败: {locator} - {e}")
            raise

    def right_click(self, locator):
        """右键点击元素"""
        try:
            self.logger.log_action("右键点击", locator)
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.actions.context_click(element).perform()
            self.logger.info(f"右键点击完成: {locator}")
        except Exception as e:
            self.logger.error(f"右键点击失败: {locator} - {e}")
            raise

    def drag_and_drop(self, source_locator, target_locator):
        """拖放元素"""
        try:
            self.logger.log_action("拖放元素", source_locator, f"到: {target_locator}")
            source = self.wait.until(EC.presence_of_element_located(source_locator))
            target = self.wait.until(EC.presence_of_element_located(target_locator))
            self.actions.drag_and_drop(source, target).perform()
            self.logger.info("拖放完成")
        except Exception as e:
            self.logger.error(f"拖放失败: {e}")
            raise

    def send_keys_with_actions(self, locator, text, clear_first=True):
        """使用ActionChains发送文本（更模拟人工输入）"""
        try:
            self.logger.log_action("模拟输入文本", locator, f"内容: {text}")
            element = self.wait.until(EC.presence_of_element_located(locator))

            if clear_first:
                element.clear()

            # 逐个字符输入，更接近人工
            self.actions.click(element).perform()
            for char in text:
                self.actions.send_keys(char).perform()
                time.sleep(0.05)  # 模拟输入间隔

            self.logger.debug(f"模拟输入完成: {locator}")
        except Exception as e:
            self.logger.error(f"模拟输入失败: {locator} - {e}")
            raise

    # ========== 3. 文件上传处理 ==========
    def upload_file(self, file_input_locator, file_path):
        """
        处理文件上传
        :param file_input_locator: <input type="file"> 元素的定位器
        :param file_path: 要上传的文件绝对路径
        """
        # 确保文件存在
        file_path_obj = Path(file_path)

        try:
            if not file_path_obj.exists():
                raise FileNotFoundError(f"要上传的文件不存在: {file_path}")

            self.logger.log_action("上传文件", file_input_locator, f"文件: {file_path}")

            # 找到文件输入元素
            file_input = self.wait.until(
                EC.presence_of_element_located(file_input_locator)
            )

            # 直接发送文件路径（适用于大多数<input type="file">）
            file_input.send_keys(str(file_path_obj.absolute()))

            self.logger.info(f"文件上传成功: {file_path_obj.name}")
            return True

        except Exception as e:
            self.logger.error(f"文件上传失败: {e}")

            # 备选方案：使用pyautogui处理弹窗式上传（需单独安装）
            try:
                import pyautogui

                self.logger.warning("尝试使用pyautogui处理文件上传弹窗")

                # 先点击文件输入框触发系统弹窗
                file_input = self.find_element(file_input_locator)
                file_input.click()
                time.sleep(1)  # 等待弹窗出现

                # 输入文件路径并确认（需根据系统调整）
                pyautogui.write(str(file_path_obj.absolute()))
                pyautogui.press("enter")
                time.sleep(1)

                self.logger.info("通过pyautogui上传成功")
                return True
            except ImportError:
                self.logger.error("pyautogui未安装，无法使用弹窗上传方案")
            except Exception as fallback_e:
                self.logger.error(f"pyautogui上传也失败: {fallback_e}")

            raise

    # ========== 4. 伪元素处理 ==========
    def get_pseudo_element_content(self, locator, pseudo_type="before"):
        """
        获取伪元素（::before, ::after）的内容
        :param locator: 宿主元素的定位器
        :param pseudo_type: 'before' 或 'after'
        :return: 伪元素的content属性值
        """
        try:
            self.logger.log_action("获取伪元素内容", locator, f"类型: {pseudo_type}")

            # 使用JavaScript获取伪元素内容
            script = """
            var element = arguments[0];
            var pseudoType = arguments[1];
            return window.getComputedStyle(element, '::' + pseudoType).getPropertyValue('content');
            """

            element = self.find_element(locator)
            content = self.driver.execute_script(script, element, pseudo_type)

            self.logger.debug(f"伪元素内容: {content}")
            return content

        except Exception as e:
            self.logger.error(f"获取伪元素内容失败: {e}")
            return None

    # ========== 5. JavaScript操作 ==========
    def execute_js(self, script, *args):
        """执行JavaScript脚本"""
        try:
            self.logger.log_action("执行JS脚本", details=f"脚本: {script[:50]}...")
            result = self.driver.execute_script(script, *args)
            self.logger.debug(f"JS执行结果: {result}")
            return result
        except JavascriptException as e:
            self.logger.error(f"JS执行失败: {e}")
            raise

    def js_click(self, locator):
        """使用JavaScript强制点击元素（绕过常规点击限制）"""
        try:
            self.logger.log_action("JS强制点击", locator)
            element = self.find_element(locator)
            self.driver.execute_script("arguments[0].click();", element)
            self.logger.info(f"JS点击完成: {locator}")
        except Exception as e:
            self.logger.error(f"JS点击失败: {locator} - {e}")
            raise

    def scroll_to_element(self, locator):
        """滚动到元素（使用JS，更平滑）"""
        try:
            self.logger.log_action("滚动到元素", locator)
            element = self.find_element(locator)

            # 使用JS滚动，带平滑效果
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element,
            )
            time.sleep(0.5)  # 等待滚动完成
            self.logger.debug(f"滚动完成: {locator}")

        except Exception as e:
            self.logger.error(f"滚动到元素失败: {locator} - {e}")
            raise

    def scroll_by_pixels(self, x_pixels=0, y_pixels=0):
        """按像素滚动页面"""
        try:
            self.logger.log_action("按像素滚动", details=f"X:{x_pixels}, Y:{y_pixels}")
            self.driver.execute_script(f"window.scrollBy({x_pixels}, {y_pixels});")
            time.sleep(0.3)
            self.logger.debug("像素滚动完成")
        except Exception as e:
            self.logger.error(f"像素滚动失败: {e}")
            raise

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        try:
            self.logger.log_action("滚动到页面底部")
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(0.5)
            self.logger.debug("已滚动到底部")
        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            raise

    def scroll_to_top(self):
        """滚动到页面顶部"""
        try:
            self.logger.log_action("滚动到页面顶部")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            self.logger.debug("已滚动到顶部")
        except Exception as e:
            self.logger.error(f"滚动到顶部失败: {e}")
            raise

    # ========== 6. 其他实用操作 ==========
    def switch_to_new_window(self, close_current=False):
        """切换到最新打开的窗口"""
        try:
            window_handles = self.driver.window_handles
            if len(window_handles) > 1:
                self.driver.switch_to.window(window_handles[-1])
                self.logger.info(f"切换到新窗口，共 {len(window_handles)} 个窗口")

                if close_current:
                    # 关闭原窗口
                    self.driver.switch_to.window(window_handles[0])
                    self.driver.close()
                    self.driver.switch_to.window(window_handles[-1])
                    self.logger.info("已关闭原窗口")

            else:
                self.logger.warning("没有新窗口可切换")
        except Exception as e:
            self.logger.error(f"切换窗口失败: {e}")
            raise

    def accept_alert(self, timeout=5):
        """接受/确认alert弹窗"""
        try:
            self.logger.log_action("接受Alert弹窗")
            wait = WebDriverWait(self.driver, timeout)
            alert = wait.until(EC.alert_is_present())
            alert_text = alert.text
            alert.accept()
            self.logger.info(f"Alert已接受，内容: {alert_text}")
            return alert_text
        except TimeoutException:
            self.logger.warning(f"{timeout}秒内未检测到Alert")
            return None
        except Exception as e:
            self.logger.error(f"处理Alert失败: {e}")
            raise

    def get_page_metrics(self):
        """获取页面性能指标"""
        try:
            metrics_script = """
            return {
                readyState: document.readyState,
                title: document.title,
                url: window.location.href,
                width: window.innerWidth,
                height: window.innerHeight,
                scrollY: window.scrollY,
                scrollX: window.scrollX
            };
            """
            metrics = self.execute_js(metrics_script)
            self.logger.debug(f"页面指标: {metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"获取页面指标失败: {e}")
            return {}
