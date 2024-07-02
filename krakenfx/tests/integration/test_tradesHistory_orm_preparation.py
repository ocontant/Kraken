import pytest_asyncio
import pytest
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.api.schemas.tradehistorySchemas import (
    SchemasTradeHistoryResponse,
    SchemasTradeHistoryResult,
    SchemasTradesReturn,
    SchemasTradeInfo
)
from krakenfx.api.models.tradeHistoryModel import (
    ModelTradeInfo as ORMTrades,
    ModelTradesHistory as ORMTradesHistory
)
from krakenfx.api.models.OrderModel import ModelOrders as ORMOrders
from krakenfx.services.account_data.tradesHistoryService import get_tradeHistory
from krakenfx.repository.storeTradeHistory import process_tradeHistory
from krakenfx.utils.logger import setup_logging
logger = setup_logging()


@pytest_asyncio.fixture(scope='function')
async def engine():
    return create_async_engine('sqlite+aiosqlite:///:memory:', future=True, echo=True)

@pytest_asyncio.fixture(scope='function', autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope='function')
async def db_session(engine):
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def display_data_model(session):
    # Display data from the order table
    results = await session.execute(text('SELECT * FROM trade_info'))
    rows = results.fetchall()
    logger.trace(f"Trades in DB: {rows}")

# The test case
@pytest.mark.asyncio
async def test_tradeHistoryService_orm_preparation(db_session):
    try:       
        logger.flow1("Starting Test")
        Trades: SchemasTradesReturn = await get_tradeHistory()
        
        # await process_orders(OrdersResult, 'open', db_session)
        await process_tradeHistory(Trades, db_session)
        await display_data_model(db_session)

        # Fetch the result using the OrderModel
        result = await db_session.get(ORMTrades, "TIOYPH-SCBGX-3VRSOE")
        if result is None:
            pytest.fail("No result found in the table trades for id 'TIOYPH-SCBGX-3VRSOE'")
    
    except TimeoutError as e:
        pytest.fail(str(e))
    except RuntimeError as e:
        pytest.fail(str(e))
    except ConnectionError as e:
        pytest.fail(str(e))
    except InvalidAPIKeyException as e:
        pytest.fail(str(e))
    except FetchResponseException as e:
        pytest.fail(str(e))
    except InvalidResponseStructureException as e:
        pytest.fail(str(e))
    except NoOrdersException as e:
        pytest.fail(str(e))
    except ValueError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(str(e))
        