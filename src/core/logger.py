#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  logger.py
@Time    :  2025/12/30 13:25:52
@Author  :  owl
@Desp    : 日志管理器
"""

import logging
import sys
import threading
from logging.handlers import RotatingFileHandler

from configs.path import LOGS_DIR


class Logger:
    """日志管理器"""

    def __init__(self, name="selenium_automation"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """配置日志处理器"""
        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_format)

        # 文件输出
        log_dir = LOGS_DIR
        log_dir.mkdir(exist_ok=True)
        # 使用实例名称作为日志文件名，保持一致性
        log_filename = f"{self.name.replace(' ', '_').replace('.', '_')}.log"
        file_handler = RotatingFileHandler(
            filename=str(log_dir / log_filename),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_format)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def log_action(self, action, locator=None, details=""):
        """记录页面操作"""
        if locator:
            message = f"{action}: {locator}"
        else:
            message = f"{action}"

        if details:
            message += f" - {details}"

        self.info(message)

    def setup_exception_logging(self):
        """设置全局异常处理器，捕获未处理的异常"""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # 允许 Ctrl+C 正常退出
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            self.logger.critical(
                "未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback)
            )

        def handle_thread_exception(args):
            self.logger.critical(
                f"线程 {args.thread.name} 中未捕获的异常",
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )

        sys.excepthook = handle_exception
        threading.excepthook = handle_thread_exception


# 全局日志实例
logger = Logger()
