import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Union

import pytz


class ErrorManager:
    def __init__(self, loggers: logging = None):
        """
        Initialize the ErrorManager.

        Parameters:
        loggers (dict): A dictionary of logger instances with keys as logger names.
        """
        self.total_errors_counter = 0
        self.error_counter = defaultdict(int)
        self.error_lists = defaultdict(list)
        self.loggers = loggers or {}

        self.started_time: datetime = datetime.now(pytz.timezone("Asia/Dubai"))

    def add_logger(self, name, logger):
        """
        Add a logger to the manager.

        Parameters:
        name (str): The name of the logger.
        logger (logging.Logger): The logger instance.
        """
        self.loggers[name] = logger

    # def add_custom_error_method(self, error_type):
    #     """
    #     Dynamically create a log method for a custom error type.

    #     Parameters:
    #     error_type (str): The custom error type.
    #     """

    #     def log_custom_error(message: Union[str, List[str]]):
    #         self.log_error(error_type, message)

    #     setattr(self, f"log_{error_type}", log_custom_error)

    def log_error(self, error_type, message: Union[str, List[str]]):
        """
        Log an error and track it.

        Parameters:
        error_type (str): The type of error.
        message (Union[str, List[str]]): The error message.
        """
        self.total_errors_counter += 1
        if error_type:
            self.error_counter[error_type] += 1

        if isinstance(message, list):
            self.error_lists[error_type].extend(message)
        else:
            self.error_lists[error_type].append(message)
        for logger in self.loggers.values():
            if isinstance(message, list):
                for msg in message:
                    logger.error(msg)
            else:
                logger.error(message)

    def log_warning(self, error_type, message: Union[str, List[str]]):
        """
        Log a warning and track it.

        Parameters:
        error_type (str): The type of warning.
        message (Union[str, List[str]]): The warning message.
        """
        if isinstance(message, list):
            self.error_lists[error_type].extend(message)
        else:
            self.error_lists[error_type].append(message)
        for logger in self.loggers.values():
            if isinstance(message, list):
                for msg in message:
                    logger.warning(msg)
            else:
                logger.warning(message)

    def log_info(self, message: Union[str, List[str]]):
        """
        Log info

        Parameters:
        info_type (str): The type of info.
        message (Union[str, List[str]]): The info message.
        """
        for logger in self.loggers.values():
            logger.info(str(message))

    def generate_summary(self, formatter):
        """
        Generate a summary of all errors, warnings, and failures.

        Parameters:
        formatter (function): A function to format the tags for titles, subtitles, and highlights.

        Returns:
        str: The summary string.
        """
        self.ended_time = datetime.now(
            pytz.timezone("Asia/Dubai")
        )  # Set end time to Dubai timezone
        duration = self.ended_time - self.started_time

        summary = f"{formatter('title', 'Summary of Execution')}\n\n"
        summary += f"{formatter('highlight', 'Started at:')} {self.started_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n"
        summary += f"{formatter('highlight', 'Ended at:')} {self.ended_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n"
        summary += f"{formatter('highlight', 'Duration:')} {duration}\n"
        summary += f"{formatter('highlight', 'Total Errors:')} {sum(self.total_errors_counter.values())}\n"
        summary += f"{formatter('highlight', 'Total Import Failures:')} {self.error_counter['validation_errors']}\n\n"

        for error_type, count in self.error_counter.items():
            summary += (
                f"{formatter('subtitle', error_type.replace('_', ' ').capitalize())}\n"
            )
            summary += f"{formatter('highlight', 'Count:')} {count}\n"
            summary += f"{formatter('highlight', 'Details:')}\n"
            for error in self.error_lists[error_type]:
                summary += f" - {error}\n"
            summary += "\n"

        return summary

    def format_console(self, tag, text):
        if tag == "title":
            return f"\033[1m\033[34m## {text}\033[0m"
        elif tag == "subtitle":
            return f"\033[1m\033[32m### {text}\033[0m"
        elif tag == "highlight":
            return f"\033[1m{text}\033[0m"
        return text

    def format_log(self, tag, text):
        if tag == "title":
            return f"## {text}"
        elif tag == "subtitle":
            return f"### {text}"
        elif tag == "highlight":
            return f"**{text}**"
        return text

    def print_summary(self):
        """
        Print the summary of all errors, warnings, and failures.
        """
        summary_console = None
        summary_log = None

        for logger in self.loggers.values():
            use_console_formatter = True
            for handler in logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    use_console_formatter = False
                    break

        if use_console_formatter:
            summary_console = self.generate_summary(self.format_console)
            print(summary_console)
        else:
            summary_log = self.generate_summary(self.format_log)
            logger.info(summary_log)

    def close_loggers(self):
        """
        Close all loggers and their handlers.
        """
        for logger in self.loggers.values():
            handlers = logger.handlers[:]
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_loggers()
