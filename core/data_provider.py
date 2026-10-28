import json
from core.api_client import APIClient
from core.config_manager import config
from core.logger import logger


class EnumDataProvider:
    """从外部系统获取枚举值，供测试用例使用"""

    _enum_cache = {}  # 缓存，避免重复请求

    @classmethod
    def fetch_enums(cls):
        """
        在用例执行前被调用，获取所有需要的枚举值。
        返回一个字典，例如 {'status': ['active', 'inactive'], 'role': ['admin', 'user']}
        """
        if cls._enum_cache:
            logger.info("Using cached enum data.")
            return cls._enum_cache

        client = APIClient()
        # 假设外部系统不需要 Token 或者有公共 Token
        enum_api_url = config.get('external_enum_api')

        try:
            response = client.get(enum_api_url)  # 注意这里 endpoint 是完整 URL 或相对路径
            # 实际项目中可能需要处理不同的响应结构
            enums = response.json().get('data', {})
            cls._enum_cache = enums

            # 也可以选择持久化到本地文件，以备离线使用
            with open('data/enum_data.json', 'w', encoding='utf-8') as f:
                json.dump(enums, f, ensure_ascii=False)

            logger.info(f"Successfully fetched enum data: {list(enums.keys())}")
            return enums
        except Exception as e:
            logger.warning(f"Failed to fetch enums from remote, trying local cache... Error: {e}")
            # 降级策略：尝试读取本地缓存文件
            try:
                with open('data/enum_data.json', 'r', encoding='utf-8') as f:
                    cls._enum_cache = json.load(f)
                logger.info("Loaded enum data from local cache.")
                return cls._enum_cache
            except FileNotFoundError:
                logger.error("No enum data available. Tests may fail.")
                return {}