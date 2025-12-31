#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  config_manager.py
@Time    :  2025/12/29 23:16:17
@Author  :  owl
@Desp    :
"""

import os
from pathlib import Path

import yaml


class AttrDict:
    """将字典转换为可以通过属性访问的对象"""

    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, AttrDict(value))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return f"AttrDict({dict.__repr__(self.__dict__)})"


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._configs = {}
        self._overrides = {}
        self._current_config = {}
        self._env = None
        self._load_configs()
        self._update_current_config()

    def _load_configs(self):
        """加载所有配置"""
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self._configs = yaml.safe_load(f)

    def set_override(self, key, value):
        """设置覆盖值"""
        self._overrides[key] = value
        self._update_current_config()

    def get_config(self, env=None):
        """获取指定环境的配置，并应用覆盖值"""
        if env is None:
            env = os.getenv("ENV", "test")

        if env not in self._configs:
            raise ValueError(f"环境 {env} 不存在")

        config = self._configs[env].copy()

        # 应用覆盖值
        config.update(self._overrides)

        return config

    def _update_current_config(self):
        """更新当前配置"""
        raw_config = self.get_config()
        # 将配置转换为可使用点号访问的对象
        self._current_config = AttrDict(raw_config)
        # self._current_config = types.SimpleNamespace(**raw_config)

    def update_env(self, env=None):
        """更新环境并重新加载配置"""
        self._env = env
        self._update_current_config()

    def __getitem__(self, key):
        """允许通过索引访问配置值"""
        if hasattr(self._current_config, key):
            return getattr(self._current_config, key)
        raise KeyError(key)

    def __getattr__(self, attr):
        """允许通过属性访问配置值"""
        if hasattr(self._current_config, attr):
            return getattr(self._current_config, attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def __str__(self):
        """魔术方法，定义对象的字符串表示"""
        return self._current_config.__repr__()

    def get(self, key, default):
        """获取配置值，支持默认值"""
        keys = key.split(".")
        value = self._current_config
        try:
            for k in keys:
                value = getattr(value, k)
            return value
        except (AttributeError, TypeError):
            return default


# 全局配置实例
config = ConfigManager()
