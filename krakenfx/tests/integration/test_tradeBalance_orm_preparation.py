import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.services.schemas.account_data.tradebalanceSchemas import (
    SchemasTradeBalanceResponse,
    SchemasTradeBalance
)
from krakenfx.repository.models.account_data.tradeBalanceModel import ModelTradeBalance as ORMTradeBalance
from krakenfx.services.account_data.tradeBalanceService import get_tradeBalance
from krakenfx.repository.storeTradeBalance import process_tradeBalance
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
    results = await session.execute(text('SELECT * FROM trade_balance'))
    rows = results.fetchall()
    logger.trace(f"Trade Balances in DB: {rows}")

# The test case
@pytest.mark.asyncio
async def test_Tradebalance_orm_preparation(db_session):
    
    try:     
        logger.flow1("Starting Test")
        # OrdersResult = OrdersResponse.result
        TradeBalances: SchemasTradeBalance = await get_tradeBalance()
        
        # await process_balance(Balances, db_session)
        await process_tradeBalance(TradeBalances, db_session)

        # Fetch the result using the OrderModel
        await display_data_model(db_session)
        result = await db_session.execute(select(ORMTradeBalance).where(ORMTradeBalance.id == 1))
        if result is None:
            pytest.fail("No result found in the table order for ID '1'")
        
    
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
        