import time
from threading import Lock
from typing import Any, Dict, Optional

from core.api_client import APIClient
from core.config_manager import config
from core.logger import logger


class TokenManager:
    """
    Token 管理器（单例），负责 Token 的获取、设置、清除与复用。

    提供的方法：
        - get_token(force_refresh=False)  获取 Token（本地缓存失效时自动调用登录接口）
        - set_token(token, ...)           手动设置 Token（如模拟不同身份）
        - clear_token()                   清除本地缓存的 Token

    用法：
        from core.token_manager import token_manager

        token = token_manager.get_token()
        token_manager.set_token("xxx")
        token_manager.clear_token()
    """

    _instance = None
    _lock = Lock()

    # 距离实际过期时间提前多少秒视为已过期，避免请求途中 Token 失效
    EXPIRE_BUFFER = 60

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialize()
                    cls._instance = instance
        return cls._instance

    def _initialize(self):
        self._token: Optional[str] = None
        self._token_type: str = "Bearer"
        self._expires_at: float = 0.0
        self._client: Optional[APIClient] = None

    # ------------------------------------------------------------------ #
    # 属性
    # ------------------------------------------------------------------ #
    @property
    def client(self) -> APIClient:
        """共享的 APIClient，Token 变更后会自动同步到其请求头"""
        if self._client is None:
            self._client = APIClient()
            if self._token:
                self._client.set_token(self._token, self._token_type)
        return self._client

    @property
    def token(self) -> Optional[str]:
        """当前缓存的 Token（可能为空）"""
        return self._token

    @property
    def auth_header(self) -> Dict[str, str]:
        """可直接用于请求的认证请求头"""
        if not self._token:
            return {}
        return {"Authorization": f"{self._token_type} {self._token}"}

    def is_valid(self) -> bool:
        """本地缓存的 Token 是否存在且在有效期内"""
        return bool(self._token) and time.time() < (self._expires_at - self.EXPIRE_BUFFER)

    # ------------------------------------------------------------------ #
    # 核心方法
    # ------------------------------------------------------------------ #
    def get_token(self, force_refresh: bool = False) -> str:
        """
        获取 Token：
        1. 本地缓存有效时直接复用，避免重复登录；
        2. 缓存不存在/已过期，或 force_refresh=True 时重新调用登录接口。
        """
        if not force_refresh and self.is_valid():
            logger.debug("Reusing cached token.")
            return self._token

        return self._login()

    def set_token(self, token: str, expires_in: Optional[int] = None,
                  token_type: str = "Bearer") -> str:
        """
        手动设置 Token，常用于：
        - 用例中需要切换身份（管理员/普通用户）
        - 登录接口返回的 Token 回写到管理器
        """
        if not token:
            raise ValueError("token 不能为空！")

        self._token = token
        self._token_type = token_type or "Bearer"
        self._expires_at = time.time() + expires_in if expires_in else float("inf")

        self.client.set_token(self._token, self._token_type)
        logger.info("Token has been set.")
        return self._token

    def clear_token(self) -> None:
        """清除本地缓存的 Token，同时移除请求头中的认证信息"""
        self._token = None
        self._expires_at = 0.0

        if self._client is not None:
            self._client.clear_token()

        logger.info("Token has been cleared.")

    # ------------------------------------------------------------------ #
    # 内部方法
    # ------------------------------------------------------------------ #
    def _login(self) -> str:
        """调用登录接口获取 Token"""
        login_conf = config.get("login") or {}
        login_url = login_conf.get("url", "/iam/api/base/login")
        payload = {
            "username": login_conf.get("username"),
            "password": login_conf.get("password"),
        }

        logger.info(f"Fetching token from {login_url} ...")
        response = self.client.post(login_url, json=payload)
        data: Dict[str, Any] = response.json()

        token = self._extract_token(data)
        if not token:
            raise RuntimeError(f"Failed to obtain authentication token, response: {data}")

        expires_in = data.get("expires_in") or (data.get("data") or {}).get("expires_in")
        token_type = data.get("token_type", "Bearer")

        self.set_token(token, expires_in=expires_in, token_type=token_type)
        logger.info("Token has been obtained successfully.")
        return self._token

    @staticmethod
    def _extract_token(data: Dict[str, Any]) -> Optional[str]:
        """兼容不同登录接口的返回结构，提取 token"""
        token_key = (config.get("login") or {}).get("token_key", "access_token")

        # 常见结构：{"access_token": "xxx"} / {"token": "xxx"} / {"data": {"access_token": "xxx"}}
        for candidate in (data, data.get("data") or {}):
            for key in (token_key, "access_token", "token"):
                value = candidate.get(key)
                if value:
                    return value
        return None


# 单例，全局直接引用
token_manager = TokenManager()
