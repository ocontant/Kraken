from dependency_injector import containers, providers

from krakenfx.di.config_container import ConfigContainer
from krakenfx.di.database_container import DatabaseContainer
from krakenfx.di.logger_container import LoggerContainer


class AppContainer(containers.DeclarativeContainer):
    config_container = providers.Container(ConfigContainer)
    logger_container = providers.Container(LoggerContainer)
    database_container = providers.Container(DatabaseContainer)
