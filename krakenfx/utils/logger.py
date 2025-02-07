import inspect
import logging
import os
from datetime import datetime

import coloredlogs

from krakenfx.utils.config import Settings


def setup_main_logging(settings: Settings):
    # Define custom logging levels
    TRACE_LEVEL_NUM = 5
    FLOW1_LEVEL_NUM = 25
    FLOW2_LEVEL_NUM = 15

    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logging.addLevelName(FLOW1_LEVEL_NUM, "FLOW1")
    logging.addLevelName(FLOW2_LEVEL_NUM, "FLOW2")

    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, message, args, **kwargs)

    def flow1(self, message, *args, **kwargs):
        if self.isEnabledFor(FLOW1_LEVEL_NUM):
            self._log(FLOW1_LEVEL_NUM, message, args, **kwargs)

    def flow2(self, message, *args, **kwargs):
        if self.isEnabledFor(FLOW2_LEVEL_NUM):
            self._log(FLOW2_LEVEL_NUM, message, args, **kwargs)

    logging.Logger.trace = trace
    logging.Logger.flow1 = flow1
    logging.Logger.flow2 = flow2

    # Handle custom log levels explicitly
    custom_levels = {
        "TRACE": TRACE_LEVEL_NUM,
        "FLOW1": FLOW1_LEVEL_NUM,
        "FLOW2": FLOW2_LEVEL_NUM,
    }

    try:
        # Get log level from settings
        log_level = settings.LOGGING_LEVEL.upper()
    except AttributeError:
        # Use 'INFO' as default if LOGGING_LEVEL is not set
        log_level = "INFO"

    numeric_level = custom_levels.get(log_level, None)
    if numeric_level is None:
        numeric_level = getattr(logging, log_level, logging.INFO)

    # Set the log level for the root logger explicitly
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Configure basic logging
    logging.basicConfig(
        level=numeric_level, format="%(levelname)s - %(name)s: %(message)s"
    )

    # Configure coloredlogs with custom color settings
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "trace": {"color": "blue"},
        "flow1": {"color": "yellow"},
        "flow2": {"color": "yellow"},
        "debug": {"color": "cyan"},
        "info": {"color": "green"},
        "warning": {"color": "yellow"},
        "error": {"color": "red"},
        "critical": {"color": "magenta"},
    }

    coloredlogs.DEFAULT_FIELD_STYLES = {
        "asctime": {"color": "green"},
        "hostname": {"color": "magenta"},
        "levelname": {"bold": True, "color": "black"},
        "name": {"color": "white"},
        "programname": {"color": "cyan"},
        "username": {"color": "yellow"},
    }

    # Apply coloredlogs to the root logger
    coloredlogs.install(level=numeric_level, logger=root_logger)

    # Ensure specific loggers do not propagate to the root logger
    specific_loggers = ["aiosqlite", "asyncio", "sqlalchemy"]
    for logger_name in specific_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)
        coloredlogs.install(
            level=numeric_level,
            fmt="%(levelname)s - %(name)s: %(message)s",
            logger=logger,
        )

    # Identify the caller module
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    caller_module = module.__name__ if module else "Unknown"

    logger = logging.getLogger(caller_module)
    logger.setLevel(numeric_level)
    coloredlogs.install(
        level=numeric_level, fmt="%(levelname)s - %(name)s: %(message)s", logger=logger
    )

    current_level = logging.getLevelName(logger.getEffectiveLevel())
    logger.info(f"Current log level: {current_level}")

    return logger


def setup_custom_logging(loggername: str, LOG_DIR: str = None, noscreen: bool = False):
    local_logger = logging.getLogger(loggername)

    # Remove existing handlers if they exist
    while local_logger.hasHandlers():
        local_logger.removeHandler(local_logger.handlers[0])

    if LOG_DIR:
        current_date = datetime.now().strftime("%Y%m%d")
        log_file_path = os.path.join(LOG_DIR, f"{current_date}-{loggername}.log")
        local_handler = logging.FileHandler(log_file_path)

        # Create and set formatter
        local_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        local_handler.setFormatter(local_formatter)

        # Add handler to logger
        local_logger.addHandler(local_handler)
    else:
        # Ensure a default handler is added if no LOG_DIR is provided
        local_handler = logging.StreamHandler()
        local_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        local_handler.setFormatter(local_formatter)
        local_logger.addHandler(local_handler)

    local_logger.setLevel(logging.INFO)
    if noscreen:
        local_logger.handlers = [
            handler
            for handler in local_logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
    return local_logger


def release_logger(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
