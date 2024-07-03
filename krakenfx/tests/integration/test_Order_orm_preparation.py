import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.api.schemas.account_data.OrderSchemas import (
    SchemasOrdersResponse,
    SchemasOrdersResult,
    SchemasOrder
)
from krakenfx.api.models.account_data.OrderModel import (
    ModelOrders as ORMOrder,
    ModelOrdersDescription as ORMOrderDescription
)
from krakenfx.services.account_data.OrderService import get_Orders
from krakenfx.repository.storeOrders import process_orders
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
    results = await session.execute(text('SELECT * FROM orders'))
    rows = results.fetchall()
    logger.trace(f"Order in DB: {rows}")

    # Display data from the order_descriptions table
    descr_results = await session.execute(text('SELECT * FROM orders_descriptions'))
    descr_rows = descr_results.fetchall()
    logger.trace(f"Order Descriptions in DB: {descr_rows}")

# The test case
@pytest.mark.asyncio
async def test_OrderService_orm_preparation(db_session):
    order_data = {
        "error": [],
        "result": {
            "closed": {
                "O66CFS-PILNI-MEQWTR": {
                    "refid": "OT12345-ABC",
                    "userref": "12345",
                    "status": "closed",
                    "opentm": 1717608049.2375944,
                    "starttm": 0,
                    "expiretm": 0,
                    "descr": {
                        "pair": "XXBTZUSD",
                        "type": "buy",
                        "ordertype": "market",
                        "price": "45000.0",
                        "price2": "0.0",
                        "leverage": "none",
                        "order": "buy 2.00000000 XXBTUSD @ market",
                        "close": "sell 2.00000000 XXBTUSD @ 50000.0"
                    },
                    "vol": "2.00000000",
                    "vol_exec": "0.00000000",
                    "cost": "90000.0",
                    "fee": "90.0",
                    "price": "45000.0",
                    "stopprice": "0.0",
                    "limitprice": "0.0",
                    "misc": "",
                    "oflags": "fciq",
                    "trades": ["TT12345", "TT67890"]
                },
                "O77DGT-QJMOJ-NFRXUS": {
                    "refid": "1T12345-ABC",
                    "userref": "67891",
                    "status": "closed",
                    "opentm": 1717608049.2375944,
                    "starttm": 0,
                    "expiretm": 0,
                    "descr": {
                        "pair": "XXBTZUSD",
                        "type": "buy",
                        "ordertype": "market",
                        "price": "52000.0",
                        "price2": "0.0",
                        "leverage": "none",
                        "order": "buy 2.00000000 XXBTUSD @ market",
                        "close": "sell 2.00000000 XXBTUSD @ 50000.0"
                    },
                    "vol": "2.00000000",
                    "vol_exec": "0.00000000",
                    "cost": "90000.0",
                    "fee": "90.0",
                    "price": "55000.0",
                    "stopprice": "0.0",
                    "limitprice": "0.0",
                    "misc": "",
                    "oflags": "fciq",
                    "trades": ["TT67891", "TT13463"]
                }
            }
        }
    }

    try:
        order_status = 'closed'
        
        logger.flow1("Starting Test")
        # OrdersResult = OrdersResponse.result
        Orders: SchemasOrdersResult = await get_Orders(order_status)
        
        # await process_orders(OrdersResult, 'open', db_session)
        await process_orders(Orders, db_session)
        await display_data_model(db_session)

        # Fetch the result using the OrderModel
        result = await db_session.execute(select(ORMOrder).where(ORMOrder.id == "O4AGJU-R6VH2-IY3ZC5"))
        if result is None:
            pytest.fail("No result found in the table order for id 'O4AGJU-R6VH2-IY3ZC5'")
        
        result_descr = await db_session.execute(select(ORMOrderDescription).where(ORMOrderDescription.id == "O4AGJU-R6VH2-IY3ZC5"))
        if result_descr is None:
            pytest.fail("No result found in the table order_descriptions for id 'O4AGJU-R6VH2-IY3ZC5'")
        
        assert result.refid is None
        assert result.userref == "0"
        assert result.status == "closed"
        assert result.opentm == 1717764389.579987
        assert result_descr.pair == "XBTUSD"
        assert result_descr.type == "buy"
        assert result_descr.ordertype == "market"
        assert result_descr.price == "0"
        assert result_descr.price2 == "0"
        assert result_descr.leverage == "5:1"
        assert result_descr.order == "buy 1.00000000 XBTUSD @ market with 5:1 leverage"
        assert result_descr.close == ""
        assert result.vol == "1.00000000"
        assert result.vol_exec == "1.00000000"
        assert result.cost == "70853.50000"
        assert result.fee == "102.73757"
        assert result.price == "70853.5"
        assert result.stopprice == "0.00000"
        assert result.limitprice == "0.00000"
        assert result.misc == ""
        assert result.oflags == "fciq"
        assert result.margin == "1"
        assert result.reason is None
        assert result.closetm == 1717764389.5800576
    
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
        