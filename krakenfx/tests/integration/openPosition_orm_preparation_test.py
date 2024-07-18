# tests/test_open_position_service.py
import logging

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from krakenfx.core.database import Base
from krakenfx.repository.models.openPositionModel import (
    ModelConsolidatedOpenPosition as ORMConsolidatedOpenPosition,
)
from krakenfx.repository.models.openPositionModel import (
    ModelOpenPosition as ORMOpenPosition,
)
from krakenfx.repository.storeOpenPositions import process_openPositions
from krakenfx.services.account_data.openPositionService import get_openPositions
from krakenfx.services.account_data.schemas.openPositionSchemas import (
    SchemasOpenPositionReturn,
)
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
)
from krakenfx.utils.logger import setup_logging

logger = setup_logging()
logging.getLogger("aiosqlite").setLevel(logging.WARNING)


@pytest_asyncio.fixture(scope="module")
async def engine():
    return create_async_engine("sqlite+aiosqlite:///:memory:", future=True, echo=True)


@pytest_asyncio.fixture(scope="module", autouse=True)
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
    results = await session.execute(text("SELECT * FROM open_positions"))
    rows = results.fetchall()
    logger.trace(f"Open Positions in DB: {rows}")

    # Display data from the order_descriptions table
    consolidated_results = await session.execute(
        text("SELECT * FROM consolidated_open_positions")
    )
    consolidated_rows = consolidated_results.fetchall()
    logger.trace(f"Consolidated Open Positions in DB: {consolidated_rows}")


# The test case
@pytest.mark.asyncio
async def test_openPositionService_orm_preparation(db_session):
    """open_position_data = {
        "TJGTYN-YATBW-KW2IWD": {
            "ordertxid": "O66CFS-PILNI-MEQWTR",
            "posstatus": "open",
            "pair": "XXBTZUSD",
            "time": 1717608049.2375944,
            "type": "buy",
            "ordertype": "market",
            "cost": "142944.20000",
            "fee": "207.26909",
            "vol": "2.00000000",
            "vol_closed": "0.00000000",
            "margin": "28588.84000",
            "terms": "0.0250% per 4 hours",
            "rollovertm": "1717708849",
            "value": "141565.90000",
            "net": "-1378.3000",
            "misc": "",
            "oflags": "",
        }
    }

    consolidated_open_position_data = {
        "pair": "XXBTZUSD",
        "positions": "3",
        "type": "buy",
        "leverage": "5.00000",
        "cost": "153772.59618",
        "fee": "130.18498",
        "vol": "2.50000000",
        "vol_closed": "0.00000000",
        "margin": "30754.51924",
        "value": "153658.12500",
        "net": "-114.4711",
    }"""

    try:
        logger.flow1("Starting Test")

        OpenPositionsReturn: SchemasOpenPositionReturn = await get_openPositions()

        await process_openPositions(OpenPositionsReturn, db_session)
        await display_data_model(db_session)

        result = await db_session.execute(
            select(ORMOpenPosition).where(
                ORMOpenPosition.trade_id == "TPI24B-V433V-QQLOHG"
            )
        )
        if result is None:
            pytest.fail(
                "No result found in the table open_positions for id 'TPI24B-V433V-QQLOHG'"
            )

        result = await db_session.execute(
            select(ORMConsolidatedOpenPosition).where(
                ORMConsolidatedOpenPosition.pair == "XXBTZUSD"
            )
        )
        if result is None:
            pytest.fail(
                "No result found in the table consolidated_open_positions for pair 'XXBTZUSD"
            )

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
    except KrakenNoOrdersException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
