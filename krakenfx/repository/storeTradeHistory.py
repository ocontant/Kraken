# krakenfx/scripts/fetch_trade_history.py
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from krakenfx.utils.utils import object_as_dict
from krakenfx.utils.errors import *
from krakenfx.api.schemas.account_data.tradehistorySchemas import (
    SchemasTradeHistoryResponse,
    SchemasTradeHistoryResult,
    SchemasTradesReturn,
    SchemasTradeInfo
    )
from krakenfx.api.models.account_data.tradeHistoryModel import (
    ModelTradeInfo as ORMTradeInfo,
    ModelTradesHistory as ORMTradeHistory
    )
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@handle_errors
async def process_tradeHistory(Trades: SchemasTradesReturn, session: AsyncSession):
    logger.info("Processing trades history.")
    
    for trade_id, Trade in Trades.items():
        logger.trace("L> Variable: process_tradeHistory(_ForLoop).Trades:\n{}".format(json.dumps(Trade.model_dump(), indent=4, default=str)))
        await store_trade(trade_id, Trade, session)
    
    logger.flow1("Completed last order ")
    logger.info("Adding Trades to database.")
    await session.commit()

async def store_trade(trade_id: str, trade: SchemasTradeInfo, session: AsyncSession):
    logger.flow1(f"Processing Trade ID: {trade_id}")

    # Check if the trade history exists in the database
    resultTradeHistory = await session.execute(select(ORMTradeHistory).where(ORMTradeHistory.id == trade_id))
    orm_trade_history = resultTradeHistory.scalar_one_or_none()

    resultTradeInfo = await session.execute(select(ORMTradeInfo).where(ORMTradeInfo.id == trade_id))
    orm_tradeInfo = resultTradeInfo.scalar_one_or_none()

    if orm_trade_history and orm_tradeInfo:
        # Trade History exists, update only the trade fields that are different
        logger.flow2(f"Trade ID {trade_id} found. Updating trade.")

        trade_dict = trade.model_dump()
        for key, value in trade_dict.items():
            if hasattr(orm_trade_history, key) and getattr(orm_trade_history, key) != value:
                setattr(orm_trade_history, key, value)
                logger.trace(f"L-> Trade ID {trade_id} - Field {key} updated to {value}")
            elif hasattr(orm_tradeInfo, key) and getattr(orm_tradeInfo, key) != value:
                setattr(orm_tradeInfo, key, value)
                logger.trace(f"L-> TradeInfo ID {orm_trade_history.tradeinfo_id} - Field {key} updated to {value}")

        logger.flow2(f"Trade ID {trade_id} updated.")   
    else:
        # Trade doesn't exist, create new trade
        logger.flow2(f"Trade ID {trade_id} not found. Creating new trade.")

        orm_tradeInfo = await create_orm_tradeInfo(trade_id, trade)
        logger.trace("L-> Variable: store_trade().orm_tradeInfo:\n{}".format(json.dumps(object_as_dict(orm_tradeInfo), indent=4, default=str)))
        logger.trace(f"Table name of {orm_tradeInfo.__class__.__name__}: {orm_tradeInfo.__tablename__}")
        logger.flow2(f"L-> Adding TradeInfo ID {orm_tradeInfo.id} to session.")
        session.add(orm_tradeInfo)

        orm_trade_history = await create_orm_tradeHistory(trade_id, trade, orm_tradeInfo)
        logger.trace("L-> Variable: store_trade().orm_trade_history:\n{}".format(json.dumps(object_as_dict(orm_trade_history), indent=4, default=str)))
        logger.trace(f"Table name of {orm_trade_history.__class__.__name__}: {orm_trade_history.__tablename__}")
        logger.flow2(f"L-> Adding TradeHistory ID {orm_trade_history.id} to session.")
        session.add(orm_trade_history)
    
    await session.flush()
    logger.flow1(f"L-> Finished processing Trade ID {trade_id}.")

async def create_orm_tradeInfo(trade_id: str, trade: SchemasTradeInfo) -> ORMTradeInfo:
    orm_trade_info = ORMTradeInfo(id=trade_id)
    trade_dict = trade.model_dump()

    for key, value in trade_dict.items():
        if hasattr(orm_trade_info, key):
            setattr(orm_trade_info, key, value)

    return orm_trade_info

async def create_orm_tradeHistory(trade_id: str, trade: SchemasTradeInfo, orm_tradeInfo: ORMTradeInfo) -> ORMTradeHistory:
    orm_trade_history = ORMTradeHistory(id=trade_id, tradeinfo_id=orm_tradeInfo.id)
    trade_dict = trade.model_dump()
    
    for key, value in trade_dict.items():
        if hasattr(orm_trade_history, key):
            setattr(orm_trade_history, key, value)

    return orm_trade_history


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
