# krakenfx/main.py
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .di.app_container import AppContainer
from .repository.storeAssetsPairs import process_asset_pairs

# Could benefit Factory design pattern
#   An attributes could be define for each repository script to define interval
#   A loop could replace import and scheduler definition
from .repository.storeBalance import process_balance
from .repository.storeLedgers import process_ledgers
from .repository.storeOpenPositions import process_openPositions
from .repository.storeOrders import process_orders
from .repository.storeTradeBalance import process_tradeBalance
from .repository.storeTradeHistory import process_tradeHistory
from .utils.logger import setup_main_logging

logger = setup_main_logging()

# Defining dependency injector pattern & Wire application components
container = AppContainer()
container.wire(
    modules=[
        "krakenfx.services.account_data.OrderService",
        "krakenfx.services.account_data.balanceService",
        "krakenfx.services.account_data.ledgerService",
        "krakenfx.services.account_data.openPositionService",
        "krakenfx.services.account_data.queryLedgersService",
        "krakenfx.services.account_data.queryOrdersService",
        "krakenfx.services.account_data.queryTradesService",
        "krakenfx.services.account_data.tradeBalanceService",
        "krakenfx.services.account_data.tradeVolumeService",
        "krakenfx.services.account_data.tradesHistoryService",
        "krakenfx.services.spot_market_data.getAssetsPairsService",
        "krakenfx.services.spot_market_data.getAssetsService",
        "krakenfx.services.spot_market_data.getDepthService",
        "krakenfx.services.spot_market_data.getSpreadsService",
        "krakenfx.services.spot_market_data.getSystemStatusService",
        "krakenfx.services.spot_market_data.getTickerService",
        "krakenfx.services.spot_market_data.getTimeService",
        "krakenfx.services.spot_market_data.getTradesService",
    ]
)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_balance, "interval", minutes=60)
    scheduler.add_job(process_tradeBalance, "interval", minutes=60)
    scheduler.add_job(process_tradeHistory, "interval", minutes=60)
    scheduler.add_job(process_orders, "interval", minutes=60)
    scheduler.add_job(process_ledgers, "interval", minutes=60)
    scheduler.add_job(process_openPositions, "interval", minutes=10)
    scheduler.add_job(process_asset_pairs, "interval", minutes=720)
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the script running
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    asyncio.run(main())
