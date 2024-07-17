import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from krakenfx.core.database import Base
from krakenfx.repository.models.ledgerModel import ModelLedger as ORMLedger
from krakenfx.repository.storeLedgers import process_ledgers
from krakenfx.services.account_data.ledgerService import get_ledgers
from krakenfx.services.account_data.schemas.ledgerSchemas import SchemasLedgers
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
)
from krakenfx.utils.logger import setup_logging

logger = setup_logging()


@pytest_asyncio.fixture(scope="function")
async def engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:", future=True, echo=True)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
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
        Ledgers: SchemasLedgers = await get_ledgers()

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
    except KrakenNoOrdersException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
