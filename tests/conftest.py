import pytest

from core.data_provider import EnumDataProvider
from core.logger import logger
from core.token_manager import token_manager


@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """
    测试套件级 Fixture。
    配置加载与 Token 获取已在根目录 conftest.py 的 global_token 中完成，
    这里只负责补充本套件需要的枚举数据。
    """
    logger.info("=== Test Suite Setup Started ===")

    enum_data = EnumDataProvider.fetch_enums()
    pytest.enum_data = enum_data  # 挂载到 pytest 模块上

    logger.info("=== Test Suite Setup Completed ===")

    yield  # 这里是测试执行阶段

    logger.info("=== Test Suite Teardown ===")


@pytest.fixture(scope="function")
def api_client():
    """
    函数级别的 Fixture，返回已注入 Token 的 API 客户端。
    Token 由根目录 conftest.py 获取并注入，这里直接复用。
    """
    return token_manager.client


@pytest.fixture(scope="function")
def enum_data():
    """
    返回全局获取的枚举值字典。
    用例可以直接使用，如 enum_data['status']
    """
    return pytest.enum_data
