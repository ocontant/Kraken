import argparse
import asyncio
import json
import logging
import time
import urllib.parse

import httpx
from pydantic import ValidationError

from krakenfx.di.app_container import AppContainer
from krakenfx.services.spot_market_data.schemas.recentTradesSchemas import (
    SchemasRecentTradesResponse,
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
async def get_recent_trades(settings: Settings, pair: str, since: str = None):
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/Trades"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {
        "nonce": nonce,
        "pair": pair,
    }
    if since:
        data["since"] = since

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
        trades_response = SchemasRecentTradesResponse.from_response(response.json())
        await check_schemasResponse_empty(trades_response)
        asset_pair_trades = trades_response.result.get(pair, [])
        return asset_pair_trades


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
    logger.info(f"Get Recent Trades for Asset Pair: {args.asset_pair}.")
    response = await get_recent_trades(settings, args.asset_pair)
    return response


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        response = asyncio.run(main(settings, logger))
        logger.info(
            json.dumps(
                [trade.model_dump() for trade in response], indent=4, default=str
            )
        )

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
