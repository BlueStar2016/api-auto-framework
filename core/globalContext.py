# -*- coding: utf-8 -*-
"""全局变量上下文：跨 fixture / 跨用例共享数据（token、用户ID、订单号等）"""

import threading
from typing import Any, Dict

from core.logger import logger


class GlobalContext:
    """
    全局变量管理类（单例，线程安全）。

    方法：
        - set(key, value)             设置变量
        - get(key, default=None)      获取某个变量
        - delete(key, default=None)   删除某个变量
        - get_all()                   获取所有变量
        - set_batch(data)             批量设置变量
        - clear()                     清空所有变量
        - has(key)                    判断变量是否存在

    用法：
        from core.globalContext import global_context

        global_context.set("token", "xxx")
        token = global_context.get("token")
        global_context.delete("token")
        all_vars = global_context.get_all()
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._data: Dict[str, Any] = {}
                    instance._data_lock = threading.Lock()
                    cls._instance = instance
        return cls._instance

    def set(self, key: str, value: Any) -> Any:
        """设置变量，返回被设置的值（key 已存在则覆盖）"""
        if not key:
            raise ValueError("变量名 key 不能为空！")

        with self._data_lock:
            self._data[key] = value

        logger.debug(f"Set global variable: {key}")
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """获取某个变量，不存在时返回 default"""
        with self._data_lock:
            return self._data.get(key, default)

    def delete(self, key: str, default: Any = None) -> Any:
        """删除某个变量，返回被删除的值（已合并原 pop）；不存在时返回 default"""
        with self._data_lock:
            if key not in self._data:
                return default
            value = self._data.pop(key)

        logger.debug(f"Deleted global variable: {key}")
        return value

    def get_all(self) -> Dict[str, Any]:
        """获取所有变量，返回副本（避免外部直接污染内部字典）"""
        with self._data_lock:
            return dict(self._data)

    def set_batch(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """批量设置变量"""
        if not isinstance(data, dict):
            raise TypeError(f"set_batch 需要 dict 类型，实际收到: {type(data).__name__}")

        with self._data_lock:
            self._data.update(data)

        logger.debug(f"Batch set global variables: {list(data.keys())}")
        return self.get_all()

    def clear(self) -> None:
        """清空所有变量"""
        with self._data_lock:
            self._data.clear()

        logger.debug("Cleared all global variables.")

    def has(self, key: str) -> bool:
        """判断某个变量是否存在"""
        with self._data_lock:
            return key in self._data

    def __repr__(self) -> str:
        with self._data_lock:
            return f"GlobalContext({len(self._data)} vars: {list(self._data.keys())})"


# 单例实例，全局直接引用
global_context = GlobalContext()
