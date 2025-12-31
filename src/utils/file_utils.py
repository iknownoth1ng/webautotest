#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  file_utils.py
@Time    :  2025/12/31 23:30:00
@Author  :  owl
@Desp    : 文件操作工具类
"""

import shutil
from pathlib import Path
from typing import Union


def clear_directory(path: Union[str, Path]) -> None:
    """
    清空指定目录中的所有文件和子目录

    Args:
        path: 目录路径
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return

    if not path.is_dir():
        raise ValueError(f"路径 {path} 不是一个目录")

    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def ensure_empty_directory(path: Union[str, Path]) -> None:
    """
    确保目录存在且为空

    Args:
        path: 目录路径
    """
    path = Path(path)
    if path.exists():
        if path.is_dir():
            clear_directory(path)
        else:
            raise ValueError(f"路径 {path} 已存在但不是一个目录")
    else:
        path.mkdir(parents=True, exist_ok=True)