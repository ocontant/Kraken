import time

from sqlalchemy.ext.asyncio import AsyncSession

from krakenfx.di.logger_container import LoggerContainer
from krakenfx.repository.models.tradeBalanceModel import (
    ModelTradeBalance as ORMTradeBalance,
)
from krakenfx.services.account_data.schemas.tradebalanceSchemas import (
    SchemasTradeBalance,
)
from krakenfx.utils.errors import async_handle_errors

logger = LoggerContainer().logger()


@async_handle_errors
async def process_tradeBalance(
    TradeBalance: SchemasTradeBalance, session: AsyncSession
):
    logger.info("Processing account trade balance.")

    orm_TradeBalance = ORMTradeBalance(
        timestamp=time.time(), **TradeBalance.model_dump()
    )
    session.add(orm_TradeBalance)

    logger.flow1("Completed Trade Balance")
    logger.info("Adding account Balance in the database.")
    await session.commit()


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
