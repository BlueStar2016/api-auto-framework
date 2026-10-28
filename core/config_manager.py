import os
import yaml
from typing import Any, Dict, List

from core.logger import logger

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config')


class ConfigManager:
    """管理不同环境的配置"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def available_envs() -> List[str]:
        """返回 config/ 目录下所有可用的环境名（如 ['dev', 'staging']）"""
        if not os.path.isdir(CONFIG_DIR):
            return []
        return sorted(f[:-5] for f in os.listdir(CONFIG_DIR) if f.endswith('.yaml'))

    def load_config(self, env: str = None):
        """根据环境名加载配置，优先级：入参 > 环境变量 TEST_ENV > dev"""
        if not env:
            env = os.getenv('TEST_ENV', 'dev')  # 默认 dev

        config_path = os.path.join(CONFIG_DIR, f'{env}.yaml')

        if not os.path.isfile(config_path):
            raise FileNotFoundError(
                f"未找到环境配置: {os.path.normpath(config_path)}，"
                f"可用环境: {self.available_envs()}"
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        self._config['env'] = env

        # 合并环境变量中的覆盖项（如 Jenkins/CI 传入的变量）
        self._config['base_url'] = os.getenv('BASE_URL', self._config.get('base_url'))
        logger.info(f"Loaded config for environment: {env}, base_url: {self._config['base_url']}")

    def get(self, key: str, default=None) -> Any:
        return self._config.get(key, default)


# 单例模式
config = ConfigManager()