# my_project/services/ledger_service.py
import argparse
import httpx
import time
import urllib.parse
import json
import asyncio
from sqlalchemy.future import select
from typing import List, Dict
from pydantic import ValidationError, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.utils.utils import generate_api_signature
from krakenfx.api.schemas.spot_market_data.assetsPairsSchemas import (
    SchemasFeeSchedule,
    SchemasAssetPairDetails,
    SchemasCollateralAssetDetails,
    SchemasReturnAssetPair,
    SchemasReturnCollateralAssetDetails,
    SchemasResponse
)
from krakenfx.api.models.spot_market_data.assetsPairsModel import ModelAssetsPairs
from krakenfx.utils.logger import setup_logging
logger = setup_logging()
settings = Settings()


@async_handle_errors
async def get_AssetsPairs(pair: str = None) -> dict:
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/AssetPairs"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce,
        "info": "info",
    }
    if pair:
        data["pair"] = pair
    
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    logger.trace(f"Headers Raw: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        return response.json()["result"]
    
@async_handle_errors    
async def get_AssetsPairs_from_database(session: AsyncSession) -> SchemasReturnAssetPair:
    result = await session.execute(select(ModelAssetsPairs))
    orm_asset_pairs = result.scalars().all()
    asset_pairs_data = {asset.pair_name: asset.data for asset in orm_asset_pairs}
    return SchemasReturnAssetPair.from_dict({"asset_pairs": asset_pairs_data})

async def main():

    logger.info("Fetching Asset Pairs from Kraken API!")
    parser = argparse.ArgumentParser(description="Fetch Asset Pairs")
    parser.add_argument("-q", "--pair", type=str, help="Specific asset pair to fetch", required=False)
    args = parser.parse_args()

    # Fetch asset pairs from API
    response = await get_AssetsPairs(args.pair)
    logger.info("Fetched Asset Pairs from API:")
    logger.info(json.dumps(response, indent=4, default=str))
    
if __name__ == "__main__":
    try:
        asyncio.run(main())

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