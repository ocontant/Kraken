import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.services.account_data.schemas.balanceSchemas import (
    SchemasBalanceResponse,
    SchemasAccountBalance
)
from krakenfx.repository.models.balanceModel import ModelBalance as ORMBalance
from krakenfx.services.account_data.balanceService import get_accountBalance
from krakenfx.repository.storeBalance import process_balance
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
    results = await session.execute(text('SELECT * FROM balances'))
    rows = results.fetchall()
    logger.trace(f"Balances in DB: {rows}")

# The test case
@pytest.mark.asyncio
async def test_balanceService_orm_preparation(db_session):
    
    try:     
        logger.flow1("Starting Test")
        # OrdersResult = OrdersResponse.result
        Balances: SchemasAccountBalance = await get_accountBalance()
        
        # await process_balance(Balances, db_session)
        await process_balance(Balances, db_session)

        # Fetch the result using the OrderModel
        result = await db_session.execute(select(ORMBalance).where(ORMBalance.asset == "XXBT"))
        if result is None:
            pytest.fail("No result found in the table order for asset 'XXBT'")
        await display_data_model(db_session)
    
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
        