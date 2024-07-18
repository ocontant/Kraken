import asyncio
import json

import httpx
from pydantic import ValidationError

from krakenfx.core.config import Settings
from krakenfx.services.spot_market_data.schemas.spreadsSchemas import (
    SchemasGetRecentSpreadsResponse,
)
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
    async_handle_errors,
)
from krakenfx.utils.logger import setup_main_logging
from krakenfx.utils.validations import (
    check_response_errors,
    check_schemasResponse_empty,
)

logger = setup_main_logging()
settings = Settings()


@async_handle_errors
async def get_recent_spreads(pair: str):
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


async def main():
    logger.info("Get Recent Spreads from Kraken server!")
    pair = "XXBTZUSD"
    response = await get_recent_spreads(pair)
    return response


if __name__ == "__main__":
    try:
        response = asyncio.run(main())
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
    except KrakenNoOrdersException as e:
        logger.error(e)
    except ValidationError as e:
        error = json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
