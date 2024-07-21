# krakenfx/services/ledger_service.py
import argparse
import asyncio
import json
import logging
import time
import urllib.parse

import httpx
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from krakenfx.di.app_container import AppContainer
from krakenfx.repository.models.assetsPairsModel import ModelAssetsPairs
from krakenfx.services.spot_market_data.schemas.assetsPairsSchemas import (
    SchemasReturnAssetPair,
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
from krakenfx.utils.validations import check_response_errors


@async_handle_errors
async def get_AssetsPairs(settings: Settings, pair: str = None) -> dict:
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/AssetPairs"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {
        "nonce": nonce,
        "info": "info",
    }
    if pair:
        data["pair"] = pair

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
        return response.json()["result"]


@async_handle_errors
async def get_AssetsPairs_from_database(
    session: AsyncSession,
) -> SchemasReturnAssetPair:
    result = await session.execute(select(ModelAssetsPairs))
    orm_asset_pairs = result.scalars().all()
    asset_pairs_data = {asset.pair_name: asset.data for asset in orm_asset_pairs}
    return SchemasReturnAssetPair.from_dict({"asset_pairs": asset_pairs_data})


async def main(settings: Settings, logger: logging.Logger):
    logger.info("Fetching Asset Pairs from Kraken API!")
    parser = argparse.ArgumentParser(description="Fetch Asset Pairs")
    parser.add_argument(
        "-q", "--pair", type=str, help="Specific asset pair to fetch", required=False
    )
    args = parser.parse_args()

    # Fetch asset pairs from API
    response = await get_AssetsPairs(settings, args.pair)
    logger.info("Fetched Asset Pairs from API:")
    logger.info(json.dumps(response, indent=4, default=str))


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        asyncio.run(main(settings, logger))

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
