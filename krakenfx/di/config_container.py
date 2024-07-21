from dependency_injector import containers, providers

from krakenfx.utils.config import Settings


class ConfigContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)
