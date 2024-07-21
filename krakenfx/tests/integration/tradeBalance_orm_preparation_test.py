import logging

import pytest
import pytest_asyncio
from sqlalchemy import select, text

from krakenfx.di.app_container import AppContainer
from krakenfx.repository.models._base import Base
from krakenfx.repository.models.tradeBalanceModel import (
    ModelTradeBalance as ORMTradeBalance,
)
from krakenfx.repository.storeTradeBalance import process_tradeBalance
from krakenfx.services.account_data.schemas.tradebalanceSchemas import (
    SchemasTradeBalance,
)
from krakenfx.services.account_data.tradeBalanceService import get_tradeBalance
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
    results = await session.execute(text("SELECT * FROM trade_balance"))
    rows = results.fetchall()
    logger.trace(f"Trade Balances in DB: {rows}")


# The test case
@pytest.mark.asyncio
async def test_Tradebalance_orm_preparation(db_session):
    try:
        logger.flow1("Starting Test")
        # OrdersResult = OrdersResponse.result
        settings = container.config_container().config()
        TradeBalances: SchemasTradeBalance = await get_tradeBalance(settings)

        # await process_balance(Balances, db_session)
        await process_tradeBalance(TradeBalances, db_session)

        # Fetch the result using the OrderModel
        await display_data_model(db_session)
        result = await db_session.execute(
            select(ORMTradeBalance).where(ORMTradeBalance.id == 1)
        )
        if result is None:
            pytest.fail("No result found in the table order for ID '1'")

    except TimeoutError as e:
        pytest.fail(str(e))
    except RuntimeError as e:
        pytest.fail(str(e))
    except ConnectionError as e:
        pytest.fail(str(e))
    except KrakenInvalidAPIKeyException as e:
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
