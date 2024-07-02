# krakenfx/scripts/fetch_open_orders.py
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from krakenfx.utils.errors import *
from krakenfx.utils.utils import object_as_dict
from krakenfx.services.openOrderService import get_openOrders
from krakenfx.api.schemas.openOrderSchemas import (
    SchemasOpenOrdersResponse,
    SchemasOpenOrdersResult,
    SchemasOpenOrder,
    SchemasOpenOrderDescription
    )
from krakenfx.api.models.openOrderModel import (
    ModelOpenOrder as ORMOpenOrder,
    ModelOpenOrderDescription as ORMOpenOrderDescription
    )
#from krakenfx.api.models.tradeHistoryModel import Trade as ORMTrade
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@handle_errors
async def check_openOrder_has_descr(order_id: str, openOrder: SchemasOpenOrder, field: str = 'descr'):
    if not hasattr(openOrder, field):
        raise InvalidResponseStructureException(f"openOrder {order_id} doesn't have attribute {field}")

@handle_errors
async def process_open_orders(openOrdersResult: SchemasOpenOrdersResult, session: AsyncSession):
    logger.info("Processing Open Orders.")

    if not openOrdersResult.open:
        raise InvalidResponseStructureException("openOrdersResult is empty")
    
    # Itereate all Open Orders
    for order_id, openOrder in openOrdersResult.open.items():
        logger.trace("L> Variable: process_open_orders(_ForLoop).openOrders:\n{}".format(json.dumps(openOrder.model_dump(), indent=4)))
        await check_openOrder_has_descr(order_id, openOrder)
        await store_openOrder(order_id, openOrder, session)

    logger.flow1("Completed last order ")
    # Commit the session after processing all orders
    logger.info("Adding Open Orders to database.")
    await session.commit()

@handle_errors
async def create_orm_openOrder_desc(order_id: str, openOrder_descr: SchemasOpenOrderDescription) -> ORMOpenOrderDescription:
    logger.flow2(f"L--> Create instance of ORM model ORMOpenOrderDescription for {order_id}.")
    openOrder_descr_dict = openOrder_descr.model_dump()
    openOrder_descr_dict['id'] = order_id # Add id field to schemas dict for FK order_id
    orm_openOrderDescr = ORMOpenOrderDescription(**openOrder_descr_dict)
    return orm_openOrderDescr

@handle_errors
async def create_orm_openOrder_withoutDescr(order_id: str, openOrder: SchemasOpenOrder, orm_openOrderDescr: ORMOpenOrderDescription) -> ORMOpenOrder:
    logger.flow2(f"L--> Create instance of ORM model ORMOpenOrder for {order_id}.")
    openOrder_dict = openOrder.model_dump(exclude_unset=True)
    if 'descr' in openOrder_dict:
       del openOrder_dict['descr'] # Need to remove the descr dict() descr from the schemas in preparation to ORM
    if 'trades' in openOrder_dict:
        del openOrder_dict['trades'] # Need to remove the trades list() trades from the schemas in preparation to ORM
    
    openOrder_dict['descr_id'] = orm_openOrderDescr.id # The descr_id need to be assigned for the relationship to open_order_descriptions table
    openOrder_dict['id'] = order_id # The order_id need to be assigned for the relationship to trade table
    orm_openOrder = ORMOpenOrder()
    for key, value in openOrder_dict.items():
        if hasattr(orm_openOrder, key):
            setattr(orm_openOrder, key, value)
    return orm_openOrder
    
@handle_errors
async def store_openOrder(order_id, openOrder: SchemasOpenOrder, session: AsyncSession):
    logger.flow1(f"Processing Open Order ID: {order_id}")

    # - Add open order description to session
    orm_OpenOrderDescr: ORMOpenOrderDescription = await create_orm_openOrder_desc(order_id, openOrder.descr)
    logger.trace("L-> Variable: store_openOrder().orm_OpenOrderDescr:\n{}".format(json.dumps(object_as_dict(orm_OpenOrderDescr), indent=4, default=str)))
    
    logger.flow2(f"L-> Adding Open Order Description ID {orm_OpenOrderDescr.id} to session.")
    session.add(orm_OpenOrderDescr)
    await session.flush()

    # - Add open order to session
    orm_OpenOrder: ORMOpenOrder = await create_orm_openOrder_withoutDescr(order_id, openOrder, orm_OpenOrderDescr)
    logger.trace("L-> Variable: process_open_orders().orm_OpenOrder:\n{}".format(json.dumps(object_as_dict(orm_OpenOrder), indent=4, default=str)))
    logger.trace(f"Table name of {orm_OpenOrder.__class__.__name__}: {orm_OpenOrder.__tablename__}")
    logger.flow2(f"L-> Adding Open Order ID {order_id} to session.")
    session.add(orm_OpenOrder)
    await session.flush()

    logger.flow1(f"L-> Finished processing open orders ID {order_id}.")

async def main():
    async with SessionLocal() as session:
        try:
            openOrdersResponse: SchemasOpenOrdersResponse = await get_openOrders()  
            await process_open_orders(openOrdersResponse, session)

        except TimeoutError as e:
            logger.error(f"Timeout error: {e}")
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
        except InvalidAPIKeyException as e:
            logger.error(f"Invalid API key: {e}")
        except FetchResponseException as e:
            logger.error(f"Error fetching open orders: {e}")
        except InvalidResponseStructureException as e:
            logger.error(f"Invalid response structure or no open orders found: {e}")
        except NoOrdersException as e:
            logger.error(e)
            data_json = json.dumps(openOrdersResponse.model_dump(), indent=4, default=str)
            logger.debug(f"Open Orders Data: {data_json}")
        except ValueError as e:
            logger.error(f"Failed with ValueError: {e}")
        except Exception as e:
            logger.error(f"Failed with Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
