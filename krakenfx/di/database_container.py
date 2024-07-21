# krakenfx/di/database_container.py
from dependency_injector import containers, providers

from krakenfx.di.config_container import ConfigContainer
from krakenfx.di.logger_container import LoggerContainer
from krakenfx.utils.database import DatabaseFactory


class DatabaseContainer(containers.DeclarativeContainer):
    config_container = providers.Container(ConfigContainer)
    logger_container = providers.Container(LoggerContainer)

    config = config_container.provided.config()
    logger = logger_container.provided.logger()

    database_factory = providers.Singleton(
        DatabaseFactory, settings=config, logger=logger
    )
