#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  element_locator.py
@Time    :  2025/12/30 18:12:52
@Author  :  owl
@Desp    :
'''
from typing import Tuple

from selenium.webdriver.common.by import By

from .logger import logger


class ElementLocator:
    """元素定位器封装"""

    @staticmethod
    def by_id(element_id: str) -> Tuple[str, str]:
        """通过ID定位"""
        return (By.ID, element_id)

    @staticmethod
    def by_name(name: str) -> Tuple[str, str]:
        """通过name属性定位"""
        return (By.NAME, name)

    @staticmethod
    def by_class_name(class_name: str) -> Tuple[str, str]:
        """通过class名称定位"""
        return (By.CLASS_NAME, class_name)

    @staticmethod
    def by_tag(tag_name: str) -> Tuple[str, str]:
        """通过标签名定位"""
        return (By.TAG_NAME, tag_name)

    @staticmethod
    def by_link_text(text: str) -> Tuple[str, str]:
        """通过链接文本定位"""
        return (By.LINK_TEXT, text)

    @staticmethod
    def by_partial_link_text(partial_text: str) -> Tuple[str, str]:
        """通过部分链接文本定位"""
        return (By.PARTIAL_LINK_TEXT, partial_text)

    @staticmethod
    def by_css(css_selector: str) -> Tuple[str, str]:
        """通过CSS选择器定位"""
        return (By.CSS_SELECTOR, css_selector)

    @staticmethod
    def by_xpath(xpath: str) -> Tuple[str, str]:
        """通过XPath定位"""
        return (By.XPATH, xpath)

    @staticmethod
    def build_xpath_with_text(element_tag: str, text: str, partial: bool = False) -> str:
        """
        构建包含文本的XPath

        Args:
            element_tag: 元素标签名，如div、a、button等
            text: 文本内容
            partial: 是否模糊匹配（包含文本）

        Returns:
            XPath字符串
        """
        if partial:
            return f"//{element_tag}[contains(text(), '{text}')]"
        else:
            return f"//{element_tag}[text()='{text}']"

    @staticmethod
    def build_xpath_with_attribute(element_tag: str, attribute: str, value: str, partial: bool = False) -> str:
        """
        构建包含属性的XPath

        Args:
            element_tag: 元素标签名
            attribute: 属性名
            value: 属性值
            partial: 是否模糊匹配

        Returns:
            XPath字符串
        """
        if partial:
            return f"//{element_tag}[contains(@{attribute}, '{value}')]"
        else:
            return f"//{element_tag}[@{attribute}='{value}']"

    @staticmethod
    def build_css_with_attribute(attribute: str, value: str) -> str:
        """
        构建CSS属性选择器

        Args:
            attribute: 属性名
            value: 属性值

        Returns:
            CSS选择器字符串
        """
        return f"[{attribute}='{value}']"

    @staticmethod
    def build_css_with_class(class_name: str) -> str:
        """
        构建CSS类选择器

        Args:
            class_name: 类名

        Returns:
            CSS选择器字符串
        """
        return f".{class_name}"

    @staticmethod
    def get_parent_locator(locator: Tuple[str, str]) -> Tuple[str, str]:
        """
        获取父元素定位器

        Args:
            locator: 原始定位器

        Returns:
            父元素定位器
        """
        by_type, selector = locator
        if by_type == By.XPATH:
            return (By.XPATH, f"{selector}/..")
        elif by_type == By.CSS_SELECTOR:
            return (By.CSS_SELECTOR, f"{selector} > *")
        else:
            # 其他定位方式转换为XPath获取父元素
            return (By.XPATH, f"({selector_to_xpath(locator)})/..")

    @staticmethod
    def get_child_locator(parent_locator: Tuple[str, str], child_locator: Tuple[str, str]) -> Tuple[str, str]:
        """
        获取子元素定位器

        Args:
            parent_locator: 父元素定位器
            child_locator: 子元素定位器

        Returns:
            子元素相对父元素的定位器
        """
        parent_by, parent_selector = parent_locator
        child_by, child_selector = child_locator

        if parent_by == By.XPATH and child_by == By.XPATH:
            return (By.XPATH, f"{parent_selector}{child_selector}")
        elif parent_by == By.CSS_SELECTOR and child_by == By.CSS_SELECTOR:
            return (By.CSS_SELECTOR, f"{parent_selector} {child_selector}")
        else:
            # 混合定位方式，统一使用XPath
            parent_xpath = selector_to_xpath(parent_locator)
            child_xpath = selector_to_xpath(child_locator)
            if child_xpath.startswith('//'):
                child_xpath = child_xpath[1:]  # 去掉开头的//
            return (By.XPATH, f"{parent_xpath}{child_xpath}")

    @staticmethod
    def get_sibling_locator(locator: Tuple[str, str], sibling_offset: int = 1) -> Tuple[str, str]:
        """
        获取兄弟元素定位器

        Args:
            locator: 原始元素定位器
            sibling_offset: 兄弟偏移量，1表示下一个兄弟，-1表示上一个兄弟

        Returns:
            兄弟元素定位器
        """
        by_type, selector = locator
        if by_type == By.XPATH:
            if sibling_offset >= 0:
                return (By.XPATH, f"{selector}/following-sibling::*[{sibling_offset}]")
            else:
                return (By.XPATH, f"{selector}/preceding-sibling::*[{-sibling_offset}]")
        else:
            # 转换为XPath处理
            xpath = selector_to_xpath(locator)
            if sibling_offset >= 0:
                return (By.XPATH, f"{xpath}/following-sibling::*[{sibling_offset}]")
            else:
                return (By.XPATH, f"{xpath}/preceding-sibling::*[{-sibling_offset}]")

    @staticmethod
    def format_locator(locator: Tuple[str, str], *args, **kwargs) -> Tuple[str, str]:
        """
        格式化定位器（支持动态定位器）

        Args:
            locator: 原始定位器，可以包含占位符
            *args, **kwargs: 格式化参数

        Returns:
            格式化后的定位器
        """
        by_type, selector = locator

        # 使用format方法格式化选择器
        try:
            formatted_selector = selector.format(*args, **kwargs)
            logger.debug(f"定位器格式化: {selector} -> {formatted_selector}")
            return (by_type, formatted_selector)
        except (KeyError, IndexError) as e:
            logger.error(f"定位器格式化失败: {selector}, 错误: {e}")
            return locator


class DynamicLocator:
    """动态定位器类"""

    def __init__(self, by_type: str, selector_template: str):
        """
        初始化动态定位器

        Args:
            by_type: 定位方式
            selector_template: 选择器模板，可以包含{}
        """
        self.by_type = by_type
        self.selector_template = selector_template

    def format(self, *args, **kwargs) -> Tuple[str, str]:
        """格式化动态定位器"""
        selector = self.selector_template.format(*args, **kwargs)
        return (self.by_type, selector)

    def __call__(self, *args, **kwargs) -> Tuple[str, str]:
        """使对象可调用"""
        return self.format(*args, **kwargs)


# 工具函数
def selector_to_xpath(locator: Tuple[str, str]) -> str:
    """
    将各种定位器转换为XPath

    Args:
        locator: 定位器元组

    Returns:
        XPath字符串
    """
    by_type, selector = locator

    if by_type == By.ID:
        return f"//*[@id='{selector}']"
    elif by_type == By.NAME:
        return f"//*[@name='{selector}']"
    elif by_type == By.CLASS_NAME:
        # 注意：class可能有多个，用contains
        return f"//*[contains(@class, '{selector}')]"
    elif by_type == By.TAG_NAME:
        return f"//{selector}"
    elif by_type == By.LINK_TEXT:
        return f"//a[text()='{selector}']"
    elif by_type == By.PARTIAL_LINK_TEXT:
        return f"//a[contains(text(), '{selector}')]"
    elif by_type == By.CSS_SELECTOR:
        # 简单转换，复杂的CSS选择器转换可能需要更复杂的逻辑
        # 这里只处理简单情况
        if selector.startswith('.'):
            # 类选择器
            class_name = selector[1:]
            return f"//*[contains(@class, '{class_name}')]"
        elif selector.startswith('#'):
            # ID选择器
            element_id = selector[1:]
            return f"//*[@id='{element_id}']"
        else:
            # 其他情况，直接作为标签名处理
            return f"//{selector}"
    elif by_type == By.XPATH:
        return selector
    else:
        return selector


def locate_element_by_text(driver, text: str, element_type: str = "*", exact: bool = True) -> Tuple[str, str]:
    """
    通过文本定位元素（快捷方法）

    Args:
        driver: WebDriver实例
        text: 文本内容
        element_type: 元素类型，如div、a、button等
        exact: 是否精确匹配

    Returns:
        定位器元组
    """
    locator = ElementLocator()
    if exact:
        xpath = locator.build_xpath_with_text(element_type, text, partial=False)
    else:
        xpath = locator.build_xpath_with_text(element_type, text, partial=True)

    logger.info(f"通过文本定位: {text}, 元素类型: {element_type}, 精确: {exact}")
    return (By.XPATH, xpath)

# 常用定位器快捷方式
id = ElementLocator.by_id
name = ElementLocator.by_name
css = ElementLocator.by_css
xpath = ElementLocator.by_xpath
class_name = ElementLocator.by_class_name
tag = ElementLocator.by_tag
link_text = ElementLocator.by_link_text
partial_link_text = ElementLocator.by_partial_link_text