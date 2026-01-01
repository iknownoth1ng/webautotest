#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  browser_video_recorder.py
@Time    :  2026/01/01 00:00:00
@Author  :  owl
@Desp    :  使用浏览器自身能力录制的视频录制工具
"""

import base64
import threading
import time
from functools import wraps

import cv2
import numpy as np

from configs.path import VIDEOS_DIR
from src.core.logger import logger


class BrowserVideoRecorder:
    """使用浏览器CDP录屏工具"""

    def __init__(self, driver, fps=30, video_name=None):
        """
        初始化录屏器
        :param driver: Selenium WebDriver
        :param fps: 帧率
        :param video_name: 视频文件名，不含扩展名
        """
        self.driver = driver
        self.fps = fps
        self.recording = False
        self.frames = []
        self.thread = None
        self.video_name = video_name or f"test_video_{int(time.time())}"
        self.video_path = VIDEOS_DIR / f"{self.video_name}.mp4"
        self.cdp_supported = self._check_cdp_support()

    def _check_cdp_support(self):
        """检查是否支持CDP命令"""
        try:
            # 尝试执行一个简单的CDP命令
            self.driver.execute_cdp_cmd("Runtime.evaluate", {"expression": "1"})
            return True
        except Exception as e:
            logger.warning(f"CDP命令不支持，可能在分布式环境中: {e}")
            logger.info("将使用桌面录屏作为备用方案")
            return False

    def start_recording(self):
        """开始录屏"""
        if self.recording:
            logger.warning("录屏已在运行中")
            return

        if not self.cdp_supported:
            logger.info("使用桌面录屏模式")
            self._start_desktop_recording()
            return

        self.recording = True
        self.frames = []
        # 启动CDP录屏
        logger.info(f"开始浏览器录屏，目标帧率: {self.fps} fps")
        self.driver.execute_cdp_cmd(
            "Page.startScreencast",
            {"format": "png", "quality": 80, "maxWidth": 1920, "maxHeight": 1080},
        )
        # 使用线程录制
        self.thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.thread.start()

    def _start_desktop_recording(self):
        """启动桌面录屏"""
        from .video_recorder import VideoRecorder

        self.desktop_recorder = VideoRecorder(fps=self.fps)
        self.desktop_recorder.start_recording()
        self.recording = True
        logger.info("开始桌面录屏")

    def stop_recording(self):
        """停止录屏"""
        if not self.recording:
            return

        if not self.cdp_supported:
            # 停止桌面录屏
            if hasattr(self, "desktop_recorder"):
                self.desktop_recorder.stop_recording(str(self.video_path))
            self.recording = False
            logger.info(f"桌面录屏结束，视频保存至: {self.video_path}")
            return

        self.recording = False
        # 停止CDP录屏
        self.driver.execute_cdp_cmd("Page.stopScreencast", {})
        # 等待线程结束
        if self.thread:
            self.thread.join(timeout=5)
        # 保存视频
        self._save_video()
        logger.info(f"浏览器录屏结束，视频保存至: {self.video_path}")

    def _capture_frames(self):
        """捕获帧"""
        frame_interval = 1.0 / self.fps
        logger.info(f"录制帧{frame_interval}")
        while self.recording:
            try:
                # 获取当前屏幕截图
                result = self.driver.execute_cdp_cmd(
                    "Page.captureScreenshot", {"format": "png", "quality": 80}
                )
                screenshot_data = result["data"]
                # 解码base64
                img_data = base64.b64decode(screenshot_data)
                # 转换为numpy数组
                nparr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    self.frames.append(frame)
                time.sleep(frame_interval)
            except Exception as e:
                logger.error(f"录制帧时出错: {e}")
                break

    def _save_video(self):
        """保存视频"""
        if not self.frames:
            logger.warning("没有帧可保存")
            return

        height, width, _ = self.frames[0].shape
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        out = cv2.VideoWriter(str(self.video_path), fourcc, self.fps, (width, height))

        for frame in self.frames:
            out.write(frame)

        out.release()
        logger.info(f"视频已保存: {self.video_path}")


def record_video(video_name=None, fps=10):
    """
    录屏装饰器
    :param video_name: 视频文件名
    :param fps: 帧率
    :return: 装饰器
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取driver，假设是关键字参数或第一个参数
            driver = kwargs.get("driver")
            if driver is None and args:
                # 尝试从args中找到driver
                for arg in args:
                    if hasattr(arg, "execute_cdp_cmd"):
                        driver = arg
                        break
            if driver is None:
                raise ValueError("未找到driver参数，无法录制视频")

            recorder = BrowserVideoRecorder(driver, fps=fps, video_name=video_name)
            recorder.start_recording()
            try:
                result = func(*args, **kwargs)
            finally:
                recorder.stop_recording()
            return result

        return wrapper

    return decorator
