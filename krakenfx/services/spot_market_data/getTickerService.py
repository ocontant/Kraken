# krakenfx/services/ticker_service.py
import asyncio
import json
import time
import urllib.parse

import httpx
from pydantic import ValidationError

from krakenfx.core.config import Settings
from krakenfx.services.spot_market_data.schemas.tickerSchemas import (
    TickerInfo,
    TickerResult,
)
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
    async_handle_errors,
)
from krakenfx.utils.logger import setup_main_logging
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.validations import (
    check_response_errors,
    check_schemasResponse_empty,
)

logger = setup_main_logging()
settings = Settings()


@async_handle_errors
async def get_ticker_information(pair: str):
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/Ticker"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {"nonce": nonce, "pair": pair}
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, headers=headers, content=urllib.parse.urlencode(data)
        )
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
    except KrakenInvalidAPIKeyException as e:
        logger.error(e)
    except KrakenFetchResponseException as e:
        logger.error(e)
    except KrakenInvalidResponseStructureException as e:
        logger.error(e)
    except KrakenNoOrdersException as e:
        logger.error(e)
    except ValidationError as e:
        error = json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
