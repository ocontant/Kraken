import argparse
import asyncio
import json
import logging

import httpx
from pydantic import ValidationError

from krakenfx.di.app_container import AppContainer
from krakenfx.services.spot_market_data.schemas.spreadsSchemas import (
    SchemasGetRecentSpreadsResponse,
)
from krakenfx.utils.config import Settings
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoItemsReturnedException,
    async_handle_errors,
)
from krakenfx.utils.validations import (
    check_response_errors,
    check_schemasResponse_empty,
)


@async_handle_errors
async def get_recent_spreads(settings: Settings, pair: str):
    urlpath = "/0/public/Spread"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    params = {
        "pair": pair,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()

        response_json = response.json()
        logger.debug(f"Response JSON: {response_json}")

        await check_response_errors(response_json)
        spreads_response = SchemasGetRecentSpreadsResponse(**response_json)
        await check_schemasResponse_empty(spreads_response)
        asset_pair_spreads = spreads_response.result.get(pair, [])
        return asset_pair_spreads


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
    logger.info("Get Recent Spreads from Kraken server!")
    response = await get_recent_spreads(settings, args.asset_pair)
    return response


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        response = asyncio.run(main(settings, logger))
        logger.info(
            json.dumps([spread.dict() for spread in response], indent=4, default=str)
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
