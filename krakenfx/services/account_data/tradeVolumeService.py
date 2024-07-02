# my_project/services/ledger_service.py
import argparse
import httpx
import time
import urllib.parse
import json
import asyncio
from typing import List
from pydantic import ValidationError
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.utils.utils import generate_api_signature
from krakenfx.api.schemas.tradeVolumeSchemas import (
    SchemasFeesMaker,
    SchemasFeesTaker,
    SchemasVolumeSubaccount,
    SchemasResult,
    SchemasResponse
    )
from krakenfx.utils.logger import setup_logging
logger = setup_logging()
settings = Settings()

assetpair = (
   "XXBTZUSD" 
)

@handle_errors
async def get_tradeVolume(assetpair: List[str] = assetpair):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/TradeVolume"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce,
        "pair": assetpair
    }
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET)
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        tradeVolumeResponse = SchemasResponse(**response.json())
        await check_schemasResponse_empty(tradeVolumeResponse)
        tradeVolumeResult = tradeVolumeResponse.result

        return tradeVolumeResult

    
async def main():
    logger.info("Query Ledger Service!")
    parser = argparse.ArgumentParser(description="Get a ledger entry information")
    parser.add_argument("-q", "--asset_pair", type=str, help="Comma delimited asset pairs to get fees information.", required=True)
    args = parser.parse_args()

    response = await get_tradeVolume(args.asset_pair)
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