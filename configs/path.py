#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  path.py
@Time    :  2025/12/29 23:18:58
@Author  :  owl
@Desp    :
"""

from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 其他路径
DRIVERS_DIR = BASE_DIR / "drivers"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
VIDEOS_DIR = REPORTS_DIR / "videos"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
DATA_DIR = BASE_DIR / "data"
