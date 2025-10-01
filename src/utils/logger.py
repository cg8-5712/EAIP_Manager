"""
日志工具
"""

import sys
import logging
from pathlib import Path

def setup_logger(name: str = "EAIP_Manager", level: str = "INFO"):
    """
    设置日志

    Args:
        name: 日志器名称
        level: 日志级别
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

# 全局日志器
logger = setup_logger()

__all__ = ['logger', 'setup_logger']
