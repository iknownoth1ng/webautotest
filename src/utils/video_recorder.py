#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  video_recorder.py
@Time    :  2025/12/31 10:15:08
@Author  :  owl
@Desp    :
"""

import threading
import time
from functools import wraps
from pathlib import Path

import cv2
import numpy as np
from PIL import ImageGrab

from configs.path import VIDEOS_DIR
from src.core.logger import logger


class VideoRecorder:
    """修复版录屏工具"""

    def __init__(self, fps=30):
        """
        初始化录屏器
        :param fps: 帧率，建议5-15之间以保证性能和文件大小
        """
        self.fps = fps
        self.recording = False
        self.frames = []  # 存储捕获的帧
        self.frame_dimensions = None  # 动态记录帧的尺寸 (宽度, 高度)
        self.thread = None

    def start_recording(self):
        """开始录屏"""
        if self.recording:
            logger.warning("录屏已在运行中")
            return

        self.recording = True
        self.frames = []
        self.frame_dimensions = None
        # 使用守护线程，确保主程序退出时能结束
        self.thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.thread.start()
        logger.info(f"开始录屏，目标帧率: {self.fps} fps")

    def _capture_frames(self):
        """捕获帧的核心循环"""
        while self.recording:
            try:
                # 捕获屏幕
                screen = ImageGrab.grab()
                frame = np.array(screen)
                # PIL 图像是 RGB 格式，OpenCV 需要 BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # 动态设置帧尺寸（使用第一帧的尺寸）
                if self.frame_dimensions is None:
                    h, w = frame.shape[:2]
                    self.frame_dimensions = (w, h)  # OpenCV 使用 (宽度, 高度)
                    logger.debug(f"动态设置帧尺寸: {self.frame_dimensions}")

                self.frames.append(frame)

                # 精确控制帧率
                time.sleep(1.0 / self.fps)

            except Exception as e:
                logger.error(f"捕获帧时发生错误: {e}")
                self.recording = False
                break

    def stop_recording(self, output_path):
        """停止录屏并保存视频文件"""
        self.recording = False

        # 等待捕获线程结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        if not self.frames:
            logger.warning("没有捕获到任何帧，视频文件将不会生成")
            return None

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # **关键修复**：使用动态获取的尺寸，而非固定值
            if self.frame_dimensions is None:
                # 如果意外没有设置尺寸，则使用第一帧的尺寸
                first_frame = self.frames[0]
                h, w = first_frame.shape[:2]
                self.frame_dimensions = (w, h)

            width, height = self.frame_dimensions

            # 选择编码器，考虑跨平台兼容性
            fourcc = cv2.VideoWriter.fourcc(*"VP80")  # 或 'avc1', 'X264'
            out = cv2.VideoWriter(
                str(output_path), fourcc, self.fps, self.frame_dimensions
            )

            if not out.isOpened():
                logger.error(f"无法初始化视频写入器，检查编码器或路径: {output_path}")
                return None

            # 写入所有帧
            frames_count = 0
            for frame in self.frames:
                # 确保帧尺寸与写入器匹配（必要时调整尺寸）
                if frame.shape[:2] != (height, width):
                    try:
                        frame = cv2.resize(frame, self.frame_dimensions)
                        logger.debug("调整帧尺寸以匹配写入器")
                    except Exception as resize_e:
                        logger.error(f"调整帧尺寸失败: {resize_e}")
                        continue

                out.write(frame)
                frames_count += 1

            out.release()
            logger.info(
                f"视频已保存: {output_path} (尺寸: {width}x{height}, 帧数: {frames_count}, 时长: {frames_count / self.fps:.1f}秒)"
            )
            return output_path

        except Exception as e:
            logger.error(f"保存视频失败: {e}")
            return None

    def get_recording_status(self):
        """获取录屏状态"""
        return {
            "recording": self.recording,
            "frames_captured": len(self.frames),
            "frame_dimensions": self.frame_dimensions,
            "estimated_duration": len(self.frames) / self.fps if self.fps > 0 else 0,
        }


def record_video(output_dir=VIDEOS_DIR, fps=15):
    """
    录屏装饰器（修复版）

    :param output_dir: 视频输出目录
    :param fps: 帧率
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 确定测试名
            test_name = func.__name__
            # 从参数中查找 driver 实例（常见于 pytest fixture）
            # driver_instance = None
            # for arg in args:
            #     if hasattr(arg, "get") and callable(getattr(arg, "get", None)):
            #         driver_instance = arg
            #         break

            # 生成带时间戳的文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            video_dir = Path(output_dir)
            video_dir.mkdir(parents=True, exist_ok=True)
            video_filename = f"{test_name}_{timestamp}.webm"
            video_path = video_dir / video_filename

            # 初始化录屏器
            recorder = VideoRecorder(fps=fps)

            # # 可选：在开始录屏前等待片刻，确保浏览器窗口在前台
            # if driver_instance:
            #     try:
            #         driver_instance.maximize_window()
            #         time.sleep(0.5)
            #     except:
            #         pass

            # 开始录屏
            recorder.start_recording()
            logger.info(f"开始为测试 '{test_name}' 录屏，文件将保存至: {video_path}")

            try:
                # 执行测试函数
                result = func(*args, **kwargs)
                return result
            except Exception as test_exception:
                # 测试失败时，记录额外信息
                logger.warning(
                    f"测试执行失败，但录屏会继续保存。错误: {test_exception}"
                )
                raise  # 重新抛出异常
            finally:
                # 确保录屏被停止并保存
                try:
                    recorder.stop_recording(video_path)

                    # 如果测试失败且视频文件存在，可以在这里将其附加到Allure报告
                    if video_path.exists() and video_path.stat().st_size > 0:
                        logger.info(
                            f"测试 '{test_name}' 录屏完成，文件大小: {video_path.stat().st_size / 1024:.1f} KB"
                        )
                        # 这里可以添加将视频附加到Allure报告的代码
                except Exception as save_error:
                    logger.error(f"保存录屏文件时发生错误: {save_error}")

        return wrapper

    return decorator
