# krakenfx/scripts/fetch_trade_history.py
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from krakenfx.di.logger_container import LoggerContainer
from krakenfx.repository.models.tradesModel import ModelTradeInfo as ORMTradeInfo
from krakenfx.services.account_data.schemas.tradesSchemas import (
    SchemasTradeInfo,
    SchemasTradesReturn,
)
from krakenfx.utils.errors import async_handle_errors
from krakenfx.utils.utils import object_as_dict

logger = LoggerContainer().logger()


@async_handle_errors
async def process_tradeHistory(Trades: SchemasTradesReturn, session: AsyncSession):
    logger.info("Processing trades history.")

    for trade_id, Trade in Trades.items():
        logger.trace(
            "L> Variable: process_tradeHistory(_ForLoop).Trades:\n{}".format(
                json.dumps(Trade.model_dump(), indent=4, default=str)
            )
        )
        await store_trade(trade_id, Trade, session)

    logger.flow1("Completed last order ")
    logger.info("Adding Trades to database.")
    await session.commit()


async def store_trade(trade_id: str, trade: SchemasTradeInfo, session: AsyncSession):
    logger.flow1(f"Processing Trade ID: {trade_id}")

    resultTradeInfo = await session.execute(
        select(ORMTradeInfo).where(ORMTradeInfo.id == trade_id)
    )
    orm_tradeInfo = resultTradeInfo.scalar_one_or_none()

    if orm_tradeInfo:
        # Trade History exists, update only the trade fields that are different
        logger.flow2(f"Trade ID {trade_id} found. Updating trade.")

        trade_dict = trade.model_dump()
        for key, value in trade_dict.items():
            if hasattr(orm_tradeInfo, key) and getattr(orm_tradeInfo, key) != value:
                setattr(orm_tradeInfo, key, value)
                logger.trace(
                    f"L-> TradeInfo ID {orm_tradeInfo.tradeinfo_id} - Field {key} updated to {value}"
                )

        logger.flow2(f"Trade ID {trade_id} updated.")
    else:
        # Trade doesn't exist, create new trade
        logger.flow2(f"Trade ID {trade_id} not found. Creating new trade.")

        orm_tradeInfo = await create_orm_tradeInfo(trade_id, trade)
        logger.trace(
            "L-> Variable: store_trade().orm_tradeInfo:\n{}".format(
                json.dumps(object_as_dict(orm_tradeInfo), indent=4, default=str)
            )
        )
        logger.trace(
            f"Table name of {orm_tradeInfo.__class__.__name__}: {orm_tradeInfo.__tablename__}"
        )
        logger.flow2(f"L-> Adding TradeInfo ID {orm_tradeInfo.id} to session.")
        session.add(orm_tradeInfo)

    await session.flush()
    logger.flow1(f"L-> Finished processing Trade ID {trade_id}.")


async def create_orm_tradeInfo(trade_id: str, trade: SchemasTradeInfo) -> ORMTradeInfo:
    orm_trade_info = ORMTradeInfo(id=trade_id)
    trade_dict = trade.model_dump()

    for key, value in trade_dict.items():
        if hasattr(orm_trade_info, key):
            setattr(orm_trade_info, key, value)

    return orm_trade_info


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
