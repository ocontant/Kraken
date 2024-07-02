import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from krakenfx.utils.utils import object_as_dict
from krakenfx.utils.errors import *
from krakenfx.api.schemas.OrderSchemas import (
    SchemasOrder,
    SchemasOrderDescription,
    SchemasOrdersResult
    )
from krakenfx.api.models.OrderModel import (
    ModelOrders as ORMOrder,
    ModelOrdersDescription as ORMOrderDescription
    )
from krakenfx.api.models.tradeHistoryModel import ModelTradeInfo as ORMTrade
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@handle_errors
# async def process_orders(OrdersResult: SchemasOrdersResult, order_status: str, session: AsyncSession):
async def process_orders(Orders: SchemasOrdersResult, session: AsyncSession):
    logger.info("Processing Orders.")

    logger.trace("L> Variable: process_orders(_ForLoop).Orders:\n{}".format(json.dumps(Orders.model_dump(), indent=4, default=str)))
    
    # Iterate all Orders
    for order_id, Order in Orders.items():
        logger.trace("L> Variable: process_orders(_ForLoop).Orders:\n{}".format(json.dumps(Order.model_dump(), indent=4, default=str)))
        await check_Order_has_descr(order_id, Order)
        await store_Order(order_id, Order, session)

    logger.flow1("Completed last order ")
    # Commit the session after processing all orders
    logger.info("Adding Orders to database.")
    await session.commit()

@handle_errors
async def check_Order_has_descr(order_id: str, Order: SchemasOrder):
    if not hasattr(Order, 'descr'):
        raise InvalidResponseStructureException(f"Order {order_id} doesn't have attribute 'descr")

@handle_errors
async def store_Order(order_id, Order: SchemasOrder, session: AsyncSession):
    logger.flow1(f"Processing Order ID: {order_id}")

    # Check if the order exists
    resultOrder = await session.execute(select(ORMOrder).where(ORMOrder.id == order_id))
    orm_order = resultOrder.scalar_one_or_none()

    resultOrderDesc = await session.execute(select(ORMOrderDescription).where(ORMOrderDescription.id == order_id))
    orm_order_descr = resultOrderDesc.scalar_one_or_none()

    if orm_order and orm_order_descr:
        # Order exists, update only the order fields that are different
        logger.flow2(f"Order ID {order_id} found. Updating order.")

        order_dict = Order.model_dump()
        order_descr: SchemasOrderDescription = order_dict.pop('descr', None)
        order_descr_dict = order_descr.model_dump()

        for key, value in order_dict.items():
            if getattr(orm_order, key) != value:
                setattr(orm_order, key, value)
                logger.trace(f"L-> Order ID {order_id} - Field {key} updated to {value}")

        for key, value in order_descr_dict.items():
            if getattr(orm_order_descr, key) != value:
                setattr(orm_order_descr, key, value)
                logger.trace(f"L-> Order Description ID {orm_order_descr.id} - Field {key} updated to {value}")

        logger.flow2(f"Order ID {order_id} updated.")
    else:
        # Order doesn't exist, create a new order
        logger.flow2(f"Order ID {order_id} not found. Creating new order.")

        # - Add order description to session
        orm_OrderDescr: ORMOrderDescription = await create_orm_Order_desc(order_id, Order.descr)
        logger.trace("L-> Variable: store_Order().orm_OrderDescr:\n{}".format(json.dumps(object_as_dict(orm_OrderDescr), indent=4, default=str)))
        logger.trace(f"Table name of {orm_OrderDescr.__class__.__name__}: {orm_OrderDescr.__tablename__}")
        logger.flow2(f"L-> Adding Order Description ID {orm_OrderDescr.id} to session.")
        
        # - Add order to session
        orm_Order: ORMOrder = await create_orm_Order_withoutDescr(order_id, Order, orm_OrderDescr)
        logger.trace("L-> Variable: process_orders().orm_Order:\n{}".format(json.dumps(object_as_dict(orm_Order), indent=4, default=str)))
        logger.trace(f"Table name of {orm_Order.__class__.__name__}: {orm_Order.__tablename__}")
        logger.flow2(f"L-> Adding Order ID {orm_Order.id} to session.")
        
        logger.flow2(f"Order ID {order_id} created.")

        session.add(orm_OrderDescr)
        session.add(orm_Order)
    
    await session.flush()
    logger.flow1(f"L-> Finished processing orders ID {order_id}.")

@handle_errors
async def create_orm_Order_desc(order_id: str, Order_descr: SchemasOrderDescription) -> ORMOrderDescription:
    logger.flow2(f"L--> Create instance of ORM model ORMOrderDescription for {order_id}.")
    Order_descr_dict = Order_descr.model_dump()
    orm_OrderDescr = ORMOrderDescription(id=order_id, **Order_descr_dict)
    return orm_OrderDescr

@handle_errors
async def create_orm_Order_withoutDescr(order_id: str, Order: SchemasOrder, orm_OrderDescr: ORMOrderDescription) -> ORMOrder:
    logger.flow2(f"L--> Create instance of ORM model ORMOrder for {order_id}.")
    Order_dict = Order.model_dump(exclude_unset=True)
    if 'descr' in Order_dict:
       del Order_dict['descr'] # Need to remove the descr dict() descr from the schemas in preparation to ORM
    if 'trades' in Order_dict:
        del Order_dict['trades'] # Need to remove the trades list() trades from the schemas in preparation to ORM
 
    orm_Order = ORMOrder(descr_id=orm_OrderDescr.id, id=order_id, **Order_dict)
    return orm_Order
    

if __name__ == "__main__":
    print("This script cannot be invoked directly!")
