import os
import sys

from loguru import logger

logger.remove()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level=LOG_LEVEL,
    enqueue=True,      
    backtrace=True,    
    diagnose=True      
)

LOG_FILE = os.getenv("LOG_FILE")
if LOG_FILE:
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=LOG_LEVEL,
        enqueue=True
    )

# Export logger instance for use throughout the app
__all__ = ["logger"]
