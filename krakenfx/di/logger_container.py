# krakenfx/di/logger_container.py
from dependency_injector import containers, providers

from krakenfx.di.config_container import ConfigContainer
from krakenfx.utils.logger import setup_main_logging


class LoggerContainer(containers.DeclarativeContainer):
    config_container = providers.Container(ConfigContainer)
    config = config_container.provided.config

    logger = providers.Singleton(setup_main_logging, settings=config)
