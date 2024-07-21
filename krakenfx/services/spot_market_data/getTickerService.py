# krakenfx/services/ticker_service.py
import argparse
import asyncio
import json
import logging
import time
import urllib.parse

import httpx
from pydantic import ValidationError

from krakenfx.di.app_container import AppContainer
from krakenfx.services.spot_market_data.schemas.tickerSchemas import (
    TickerInfo,
    TickerResult,
)
from krakenfx.utils.config import Settings
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoItemsReturnedException,
    async_handle_errors,
)
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.validations import (
    check_response_errors,
    check_schemasResponse_empty,
)


@async_handle_errors
async def get_ticker_information(settings: Settings, pair: str):
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


async def main(settings: Settings, logger: logging.Logger):
    parser = argparse.ArgumentParser(description="Get a ledger entry information")
    parser.add_argument(
        "-q",
        "--asset_pair",
        type=str,
        default="XXBTZUSD",
        help="Comma delimited asset pairs to get fees information.",
        required=False,
    )
    args = parser.parse_args()
    logger.info(
        f"Get Ticker Information for pair {args.asset_pair} from Kraken server!"
    )
    response = await get_ticker_information(settings, args.asset_pair)
    return response


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        response = asyncio.run(main(settings, logger))
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
    except KrakenNoItemsReturnedException as e:
        logger.error(e)
    except ValidationError as e:
        error = json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
