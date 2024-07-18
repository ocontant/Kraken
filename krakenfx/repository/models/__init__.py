import importlib
import pkgutil
from pathlib import Path

from sqlalchemy.orm import declarative_base

from krakenfx.utils.errors import handle_errors
from krakenfx.utils.logger import setup_main_logging

logger = setup_main_logging()

Base = declarative_base()


@handle_errors
def import_submodules(package_name):
    package = importlib.import_module(package_name)
    if hasattr(package, "__path__"):
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_name = f"{package_name}.{name}"
            logger.info(f"\n\n\n Importing submodule: {full_name}\n")
            importlib.import_module(full_name)
            if is_pkg:
                import_submodules(full_name)


@handle_errors
def log_registered_tables():
    registered_tables = Base.metadata.tables.keys()
    for table_name in registered_tables:
        logger.info(f"Registered table: {table_name}")


@handle_errors
def log_loaded_tables(context):
    loaded_tables = Base.metadata.tables.keys()
    logger.info(f"{context} Tables loaded: {', '.join(loaded_tables)}")


@handle_errors
def load_models(package_name):
    # Import all submodules in models
    import_submodules(package_name)

    # Ensure all models are registered with the Base
    base_path = Path(__file__).parent
    for file in base_path.rglob("*.py"):
        if file.name != "__init__.py" and not file.parent.name.startswith("__"):
            module_name = (
                file.with_suffix("").relative_to(base_path).as_posix().replace("/", ".")
            )
            logger.info(f"Importing model: {module_name}")
            importlib.import_module(f"{package_name}.{module_name}")

    # Log all registered tables
    log_registered_tables()


load_models(__name__)
log_loaded_tables("Module import:")
