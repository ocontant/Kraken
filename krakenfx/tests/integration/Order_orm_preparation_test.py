import logging

import pytest
import pytest_asyncio
from sqlalchemy import select, text

from krakenfx.di.app_container import AppContainer
from krakenfx.repository.models._base import Base
from krakenfx.repository.models.OrderModel import ModelOrders as ORMOrder
from krakenfx.repository.models.OrderModel import (
    ModelOrdersDescription as ORMOrderDescription,
)
from krakenfx.repository.storeOrders import process_orders
from krakenfx.services.account_data.OrderService import get_Orders
from krakenfx.services.account_data.schemas.OrderSchemas import SchemasOrdersResult
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
    results = await session.execute(text("SELECT * FROM orders"))
    rows = results.fetchall()
    logger.trace(f"Order in DB: {rows}")

    # Display data from the order_descriptions table
    descr_results = await session.execute(text("SELECT * FROM orders_descriptions"))
    descr_rows = descr_results.fetchall()
    logger.trace(f"Order Descriptions in DB: {descr_rows}")


# The test case
@pytest.mark.asyncio
async def test_OrderService_orm_preparation(db_session):
    try:
        order_status = "closed"

        logger.flow1("Starting Test")
        settings = container.config_container().config()
        Orders: SchemasOrdersResult = await get_Orders(settings, order_status)

        await process_orders(Orders, db_session)
        await display_data_model(db_session)

        # Fetch the result using the OrderModel
        result = await db_session.execute(
            select(ORMOrder).where(ORMOrder.id == "O4AGJU-R6VH2-IY3ZC5")
        )
        order = result.scalars().first()
        if order is None:
            pytest.fail(
                "No result found in the table order for id 'O4AGJU-R6VH2-IY3ZC5'"
            )

        result_descr = await db_session.execute(
            select(ORMOrderDescription).where(
                ORMOrderDescription.id == "O4AGJU-R6VH2-IY3ZC5"
            )
        )
        order_descr = result_descr.scalars().first()
        if order_descr is None:
            pytest.fail(
                "No result found in the table order_descriptions for id 'O4AGJU-R6VH2-IY3ZC5'"
            )

        assert order.refid is None
        assert order.userref == "0"
        assert order.status == "closed"
        assert order.opentm == 1717764389.579987
        assert order_descr.pair == "XBTUSD"
        assert order_descr.type == "buy"
        assert order_descr.ordertype == "market"
        assert order_descr.price == "0"
        assert order_descr.price2 == "0"
        assert order_descr.leverage == "5:1"
        assert order_descr.order == "buy 1.00000000 XBTUSD @ market with 5:1 leverage"
        assert order_descr.close == ""
        assert order.vol == "1.00000000"
        assert order.vol_exec == "1.00000000"
        assert order.cost == "70853.50000"
        assert order.fee == "102.73757"
        assert order.price == "70853.5"
        assert order.stopprice == "0.00000"
        assert order.limitprice == "0.00000"
        assert order.misc == ""
        assert order.oflags == "fciq"
        assert order.margin == "1"
        assert order.reason is None
        assert order.closetm == 1717764389.5800576

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
