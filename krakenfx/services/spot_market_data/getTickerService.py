# my_project/services/ticker_service.py
import httpx
import time
import urllib.parse
import json
import asyncio
from pydantic import ValidationError
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.api.schemas.spot_market_data.tickerSchemas import (
    TickerResult,
    TickerInfo
)
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.logger import setup_logging

logger = setup_logging()
settings = Settings()


@async_handle_errors
async def get_ticker_information(pair: str):
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/Ticker"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce,
        "pair": pair
    }
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        ticker_response = TickerResult(**response.json())
        await check_schemasResponse_empty(ticker_response)
        ticker_info: TickerInfo = ticker_response.result[pair]
        return ticker_info

    
async def main():
    pair = "XXBTZUSD"  # Example pair, change as needed
    logger.info(f"Get Ticker Information for pair {pair} from Kraken server!")
    response = await get_ticker_information(pair)
    return response

if __name__ == "__main__":
    try:
        response = asyncio.run(main())
        logger.info(json.dumps(response.model_dump(), indent=4, default=str))

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
