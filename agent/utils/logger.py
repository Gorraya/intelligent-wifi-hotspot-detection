"""
Centralized logging configuration using Loguru.
"""

import sys
from loguru import logger
from agent.config import settings


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        "logs/agent_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    )
    return logger


log = setup_logger()
