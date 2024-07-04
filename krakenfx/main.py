# my_project/main.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from krakenfx.core.database import Base
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
# Could benefit Factory design pattern
#   An attributes could be define for each repository script to define interval
#   A loop could replace import and scheduler definition
from krakenfx.repository.storeBalance import process_balance
from krakenfx.repository.storeTradeBalance import process_tradeBalance
from krakenfx.repository.storeTradeHistory import process_tradeHistory
from krakenfx.repository.storeOrders import process_orders
from krakenfx.repository.storeLedgers import process_ledgers
from krakenfx.repository.storeOpenPositions import process_openPositions
from krakenfx.repository.storeAssetsPairs import process_asset_pairs
from krakenfx.core.config import Settings
from krakenfx.utils.logger import setup_logging
logger = setup_logging()
settings = Settings()


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_balance, 'interval', minutes=60)
    scheduler.add_job(process_tradeBalance, 'interval', minutes=60)
    scheduler.add_job(process_tradeHistory, 'interval', minutes=60)
    scheduler.add_job(process_orders, 'interval', minutes=60)
    scheduler.add_job(process_ledgers, 'interval', minutes=60)
    scheduler.add_job(process_openPositions, 'interval', minutes=10)
    scheduler.add_job(process_asset_pairs, 'interval', minutes=720)
    scheduler.start()
    
    try:
        while True:
            await asyncio.sleep(3600)  # Keep the script running
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())
