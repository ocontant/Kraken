# krakenfx/services/trade_history_service.py
import httpx
import time
import urllib.parse
import json
import asyncio
from pydantic import ValidationError
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.logger import setup_logging
from krakenfx.services.account_data.schemas.tradehistorySchemas import (
    SchemasTradeHistoryResponse,
    SchemasTradeHistoryResult,
    SchemasTradesReturn,
    SchemasTradeInfo
)

settings = Settings()
logger = setup_logging()
  
@async_handle_errors
async def get_tradeHistory():
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/TradesHistory"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce
    }
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET)
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        TradeHistoryResponse = SchemasTradeHistoryResponse(**response.json())
        await check_schemasResponse_empty(TradeHistoryResponse, 'trades')
        Trades: SchemasTradesReturn = getattr(TradeHistoryResponse.result, 'trades')
        return Trades

async def main():
    logger.info("Starting TradeHistoryService!")
    response: SchemasTradesReturn = await get_tradeHistory()
    return response

if __name__ == "__main__":
    try:
        logger.info(asyncio.run(main()))
    except TimeoutError as e:
        logger.error(e)
    except RuntimeError as e:
        logger.error(e)
    except ConnectionError as e:
        logger.error(e)
    except InvalidAPIKeyException as e:
        logger.error(e)
    except FetchResponseException as e:
        logger.error(e)
    except InvalidResponseStructureException as e:
        logger.error(e)
    except NoOrdersException as e:
        logger.error(e)
    except ValidationError as e:
        error=json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)