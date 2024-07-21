import logging

import structlog
from colorama import Fore, Style


# Custom processors for structlog
class ErrorWarningCounter:
    def __init__(self):
        self.error_count = 0
        self.warning_count = 0

    def __call__(self, logger, method_name, event_dict):
        if method_name == "error":
            self.error_count += 1
        elif method_name == "warning":
            self.warning_count += 1
        return event_dict


class InMemoryLogStore:
    def __init__(self):
        self.records = []

    def __call__(self, logger, method_name, event_dict):
        self.records.append(event_dict)
        return event_dict

    def get_summary(self):
        return {
            "total_logs": len(self.records),
            "errors": sum(1 for r in self.records if r["level"] == "error"),
            "warnings": sum(1 for r in self.records if r["level"] == "warning"),
            "messages": self.records,
        }


# Custom formatter for console with colors
class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelname, Fore.WHITE)
        record.msg = color + str(record.msg) + Style.RESET_ALL
        return super().format(record)


# Structlog configuration
error_warning_counter = ErrorWarningCounter()
in_memory_log_store = InMemoryLogStore()

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        error_warning_counter,
        in_memory_log_store,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure standard logging
logging.basicConfig(level=logging.DEBUG)

# Console handler with color formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = ColorFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)

# File handler with Markdown formatter
file_handler = logging.FileHandler("app.md")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "### %(asctime)s - %(name)s - %(levelname)s\n\n%(message)s\n"
)
file_handler.setFormatter(file_formatter)

# JSON file handler
json_file_handler = logging.FileHandler("app.json")
json_file_handler.setLevel(logging.INFO)
json_file_formatter = logging.Formatter(
    '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
json_file_handler.setFormatter(json_file_formatter)

# Add handlers to the root logger
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
root_logger.addHandler(json_file_handler)

# Example usage
logger = structlog.get_logger("example_logger")

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Access the summary from in_memory_log_store
summary = in_memory_log_store.get_summary()
print(summary)
