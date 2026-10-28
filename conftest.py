import os

import pytest

from core.config_manager import config
from core.globalContext import global_context
from core.logger import logger
from core.token_manager import token_manager


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=os.getenv("TEST_ENV", "dev"),
        help=f"指定测试环境，可选: {', '.join(config.available_envs()) or 'dev'}；"
             f"未指定时取环境变量 TEST_ENV，仍为空则为 dev",
    )


@pytest.fixture(scope="session", autouse=True)
def global_token(request):
    """
    会话级 Fixture，整个测试会话只执行一次：
    1. 加载环境配置
    2. 获取 Token
    3. 将 Token 存入全局变量，供所有用例使用
    """
    logger.info("=== Global Setup Started ===")

    env = request.config.getoption("--env")
    config.load_config(env)
    global_context.set("env", env)

    token = token_manager.get_token()

    # 存入全局变量，用例中可通过 global_context.get('token') 或 token 固件获取
    global_context.set("token", token)
    logger.info("=== Global Setup Completed ===")

    yield token

    logger.info("=== Global Teardown ===")
    token_manager.clear_token()
    global_context.delete("token")


@pytest.fixture(scope="session")
def token():
    """返回全局 Token，用例直接声明该固件即可使用"""
    return global_context.get("token")


@pytest.fixture(scope="session")
def env():
    """返回当前测试环境名，如 dev / staging"""
    return global_context.get("env")


@pytest.fixture(scope="session")
def context():
    """返回全局变量上下文对象，用例可直接读写全局变量"""
    return global_context
