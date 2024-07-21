import logging

import pytest
import pytest_asyncio
from sqlalchemy import text

from krakenfx.di.app_container import AppContainer
from krakenfx.repository.models.ledgerModel import ModelLedger as ORMLedger
from krakenfx.repository.storeLedgers import process_ledgers
from krakenfx.services.account_data.ledgerService import get_ledgers
from krakenfx.services.account_data.schemas.ledgerSchemas import SchemasLedgers
from krakenfx.utils.database import Base
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoItemsReturnedException,
)

container = AppContainer()

# Retrieve the logger from the container
logger = container.logger_container().logger()
logging.getLogger("aiosqlite").setLevel(logging.WARNING)


@pytest_asyncio.fixture(scope="function")
async def engine():
    return (
        await container.database_container()
        .database_factory()
        .get_sqlite_memory_async_engine()
    )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async_session = (
        await container.database_container()
        .database_factory()
        .get_sqlite_memory_async_session_factory()
    )
    async with async_session() as session:
        yield session


async def display_data_model(session):
    # Display data from the order table
    results = await session.execute(text("SELECT * FROM ledgers"))
    rows = results.fetchall()
    logger.trace(f"Ledgers in DB: {rows}")


# The test case
@pytest.mark.asyncio
async def test_LedgerService_orm_preparation(db_session):
    try:
        logger.flow1("Starting Test")
        # OrdersResult = OrdersResponse.result
        settings = container.config_container().config()
        Ledgers: SchemasLedgers = await get_ledgers(settings)

        # await process_orders(OrdersResult, 'open', db_session)
        await process_ledgers(Ledgers, db_session)
        await display_data_model(db_session)

        # Fetch the result using the OrderModel
        result = await db_session.get(ORMLedger, "L6C6M2-JDCVB-M6EX2H")
        if result is None:
            pytest.fail(
                "No result found in the table trades for id 'L6C6M2-JDCVB-M6EX2H'"
            )

    except KrakenInvalidAPIKeyException as e:
        pytest.fail(str(e))
    except TimeoutError as e:
        pytest.fail(str(e))
    except RuntimeError as e:
        pytest.fail(str(e))
    except ConnectionError as e:
        pytest.fail(str(e))
    except KrakenFetchResponseException as e:
        pytest.fail(str(e))
    except KrakenInvalidResponseStructureException as e:
        pytest.fail(str(e))
    except KrakenNoItemsReturnedException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
