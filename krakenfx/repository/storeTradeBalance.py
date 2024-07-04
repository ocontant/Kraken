import time
from sqlalchemy.ext.asyncio import AsyncSession
from krakenfx.utils.errors import *
from krakenfx.api.schemas.account_data.tradebalanceSchemas import (
    SchemasTradeBalanceResponse,
    SchemasTradeBalance
    )
from krakenfx.api.models.account_data.tradeBalanceModel import (
    ModelTradeBalance as ORMTradeBalance
    )
from krakenfx.utils.logger import setup_logging
logger = setup_logging()

@async_handle_errors
async def process_tradeBalance(TradeBalance: SchemasTradeBalance, session: AsyncSession):
    logger.info("Processing account trade balance.")
    
    orm_TradeBalance = ORMTradeBalance(timestamp=time.time(), **TradeBalance.model_dump())
    session.add(orm_TradeBalance) 
    
    logger.flow1("Completed Trade Balance")
    logger.info("Adding account Balance in the database.")
    await session.commit()


if __name__ == "__main__":
    print("This script cannot be invoked directly!")
