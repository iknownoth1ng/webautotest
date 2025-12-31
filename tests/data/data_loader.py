#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  data_loader.py
@Time    :  2025/12/31 22:57:21
@Author  :  owl
@Desp    :
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


class DataLoader:
    """测试数据加载器"""

    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """加载YAML文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """加载CSV文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        data = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        return data

    @staticmethod
    def load_test_data(data_file: str):
        """根据文件扩展名自动加载测试数据"""
        path = Path(data_file)
        extension = path.suffix.lower()

        if extension == ".json":
            return DataLoader.load_json(data_file)
        elif extension in [".yaml", ".yml"]:
            return DataLoader.load_yaml(data_file)
        elif extension == ".csv":
            return DataLoader.load_csv(data_file)
        else:
            raise ValueError(f"不支持的文件格式: {extension}")
