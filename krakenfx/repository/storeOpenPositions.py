# krakenfx/scripts/fetch_open_positions.py
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from krakenfx.utils.utils import object_as_dict
from krakenfx.utils.errors import *
from krakenfx.api.schemas.account_data.openPositionSchemas import (
    SchemasOpenPositionResponse,
    SchemasOpenPosition,
    SchemasConsolidatedOpenPosition,
    SchemasOpenPositions,
    SchemasConsolidatedOpenPositions,
    SchemasOpenPositionReturn
)
from krakenfx.api.models.account_data.openPositionModel import (
    ModelConsolidatedOpenPosition as ORMConsolidatedOpenPosition,
    ModelOpenPosition as ORMOpenPosition
)
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@async_handle_errors
async def process_openPositions(OpenPositionReturn: SchemasOpenPositionReturn, session: AsyncSession):
    logger.info("Processing Open Positions.")

    logger.trace("L> Variable: process_openPositions(_ForLoop).OpenPositionReturn\n{}".format(json.dumps(OpenPositionReturn.openPositions, indent=4, default=str)))
    logger.trace("L> Variable: process_openPositions(_ForLoop).OpenPositionReturn\n{}".format(json.dumps(OpenPositionReturn.consolidatedOpenPositions, indent=4, default=str)))
    # Iterate open positions:
    for trade_id, openPosition in OpenPositionReturn.openPositions.items():
        logger.trace("L> Variable: process_openPositions(_ForLoop).OpenPosition\n{}".format(json.dumps(openPosition.to_json(), indent=4, default=str)))
        await store_openPosition(trade_id, openPosition, session)

    for ConsolidatedOpenPosition in OpenPositionReturn.consolidatedOpenPositions:
        logger.trace("L> Variable: process_openPositions(_ForLoop).ConsolidatedOpenPosition\n{}".format(json.dumps(ConsolidatedOpenPosition.to_json(), indent=4, default=str)))
        await store_consolidatedOpenPosition(ConsolidatedOpenPosition, session)
    
    logger.flow1("Completed all Open Positions & Consolidated Pairs")
    logger.info("Adding Open Positions to database")
    await session.commit()

@async_handle_errors
async def store_openPosition(trade_id: str, openPosition: SchemasOpenPosition, session: AsyncSession):
    logger.flow1(f"Processing Open Position Trade ID: {trade_id}")
    
    # Check if the trade history exists in the database
    resultOpenPositions = await session.execute(select(ORMOpenPosition).where(ORMOpenPosition.trade_id == trade_id))
    orm_openPosition = resultOpenPositions.scalar_one_or_none()

    if orm_openPosition:
        # Open Position exists, update only the Open Position fields that are different
        logger.flow2(f"Open Position Trade ID {trade_id} found. Updating Open Position.")

        openPositions_dict = openPosition.model_dump()
        for key, value in openPositions_dict.items():
            if hasattr(orm_openPosition, key) and getattr(orm_openPosition, key) != value:
                setattr(orm_openPosition, key, value)
                logger.trace(f"L-> Open Position Trade ID {trade_id} - Field {key} updated to {value}")
            
        logger.flow2(f"Open Position Trade ID {trade_id} updated.")   
    else:
        # Open Positoin doesn't exist, create new Open Position
        logger.flow2(f"Open Position Trade ID {trade_id} not found. Creating new Open Position.")

        orm_openPosition = await create_orm_openPosition(trade_id, openPosition)
        logger.trace("L-> Variable: store_openPosition().orm_openPosition:\n{}".format(json.dumps(object_as_dict(orm_openPosition), indent=4, default=str)))
        logger.trace(f"Table name of {orm_openPosition.__class__.__name__}: {orm_openPosition.__tablename__}")
        logger.flow2(f"L-> Adding Open Position Trade ID {orm_openPosition.trade_id} to session.")
        session.add(orm_openPosition)
    
    await session.flush()

@async_handle_errors
async def create_orm_openPosition(trade_id: str, openPosition: SchemasOpenPosition) -> ORMOpenPosition:
    orm_openPosition = ORMOpenPosition(trade_id=trade_id)
    openPosition_dict = openPosition.model_dump()

    for key, value in openPosition_dict.items():
        if hasattr(orm_openPosition, key):
            setattr(orm_openPosition, key, value)

    return orm_openPosition

@async_handle_errors
async def store_consolidatedOpenPosition(consolidatedOpenPosition: SchemasConsolidatedOpenPosition, session: AsyncSession):
    logger.flow1(f"Processing Consolidated Open Position Pair: {consolidatedOpenPosition.pair}")
    
    # Check if the trade history exists in the database
    resultConsolidatedOpenPosition = await session.execute(select(ORMConsolidatedOpenPosition).where(ORMConsolidatedOpenPosition.pair == consolidatedOpenPosition.pair))
    orm_ConsolidatedOpenPosition = resultConsolidatedOpenPosition.scalar_one_or_none()

    if orm_ConsolidatedOpenPosition:
        # Consolidated Open Position exists, update only the Open Position fields that are different
        logger.flow2(f"Consolidated Open Position Pair {orm_ConsolidatedOpenPosition.pair} found. Updating Consolidated Open Position.")

        consolidatedOpenPosition_dict = consolidatedOpenPosition.model_dump()
        for key, value in consolidatedOpenPosition_dict.items():
            if hasattr(orm_ConsolidatedOpenPosition, key) and getattr(orm_ConsolidatedOpenPosition, key) != value:
                setattr(orm_ConsolidatedOpenPosition, key, value)
                logger.trace(f"L-> Consolidated Open Position Pair {orm_ConsolidatedOpenPosition.pair} - Field {key} updated to {value}")
            
        logger.flow2(f"Consolidated Open Position Pair: {orm_ConsolidatedOpenPosition.pair} updated.")   
    else:
        # Consolidated Open Positoin doesn't exist, create new Consolidated Open Position
        logger.flow2(f"Consolidated Open Position Pair {consolidatedOpenPosition.pair} not found. Creating new Open Position.")

        orm_consolidatedOpenPosition = await create_orm_consolidatedOpenPosition(consolidatedOpenPosition)
        logger.trace("L-> Variable: store_openPosition().orm_consolidatedOpenPosition:\n{}".format(json.dumps(object_as_dict(orm_consolidatedOpenPosition), indent=4, default=str)))
        logger.trace(f"Table name of {orm_consolidatedOpenPosition.__class__.__name__}: {orm_consolidatedOpenPosition.__tablename__}")
        logger.flow2(f"L-> Adding Consolidated Open Position Pair {orm_consolidatedOpenPosition.pair} to session.")
        session.add(orm_consolidatedOpenPosition)
    
    await session.flush()

@async_handle_errors
async def create_orm_consolidatedOpenPosition(consolidatedOpenPosition: SchemasConsolidatedOpenPosition) -> ORMConsolidatedOpenPosition:
    orm_consolidatedOpenPosition = ORMConsolidatedOpenPosition(**consolidatedOpenPosition.model_dump())
    
    return orm_consolidatedOpenPosition


if __name__ == "__main__":
    print("This script cannot be invoked directly!")

