import logging
import os
import sys
from datetime import datetime

# 日志级别映射（可根据需要调整）
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# 日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Logger:
    """
    日志管理器，支持控制台和文件双输出。
    用法：
        from core.logger import logger
        logger.info("This is an info message")
        logger.error("Something went wrong")
    """

    def __init__(self, name="api_test", log_dir="reports/logs", level="DEBUG"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL_MAP.get(level.upper(), logging.DEBUG))

        # 避免重复添加 handler（防止多次初始化时重复输出）
        if not self.logger.handlers:
            # 控制台 Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # 文件 Handler（按天滚动，可自行扩展 RotatingFileHandler）
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


# 实例化一个全局可用的 logger 对象
logger = Logger().get_logger()