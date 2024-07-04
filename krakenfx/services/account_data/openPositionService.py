# krakenfx/services/open_position_service.py
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
from krakenfx.api.schemas.account_data.openPositionSchemas import (
    SchemasOpenPosition,
    SchemasConsolidatedOpenPosition,
    SchemasOpenPositions,
    SchemasConsolidatedOpenPositions,
    SchemasOpenPositionResponse,
    SchemasOpenPositionReturn
)
from krakenfx.utils.logger import setup_logging
logger = setup_logging()
settings = Settings()

@async_handle_errors
async def fetch_openPositions(docalcs: bool = False, consolidation: str = None):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/OpenPositions"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    # Base data dictionary
    data = {
        "nonce": nonce,
    }

    # Add 'docalcs' to data if the condition is met
    if docalcs:
        data["docalcs"] = True

    # Add 'consolidation' to data if the condition is met
    if consolidation and consolidation == "market":
        data["consolidation"] = consolidation
    elif not consolidation is None and consolidation != "":
        raise ValueError(f"Expected 'market' for consolidation variable, received '{consolidation}'")

    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET)
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        openPositionResponse = SchemasOpenPositionResponse(**response.json())
        return openPositionResponse

@async_handle_errors
async def get_openPositions():
    openPositionsResponse: SchemasOpenPositionResponse = await fetch_openPositions(docalcs=True, consolidation="")
    await check_schemasResponse_empty(openPositionsResponse)
    OpenPositions: SchemasOpenPositions = openPositionsResponse.result
    
    # Consolidated view
    openConsolidatedPositionResponse: SchemasOpenPositionResponse = await fetch_openPositions(docalcs=True, consolidation="market")
    await check_schemasResponse_empty(openConsolidatedPositionResponse)
    ConsolidatedopenPositions: SchemasConsolidatedOpenPositions = openConsolidatedPositionResponse.result
    
    # OpenPositionReturn view
    OpenPositionsReturn = SchemasOpenPositionReturn
    OpenPositionsReturn.openPositions = OpenPositions
    OpenPositionsReturn.consolidatedOpenPositions = ConsolidatedopenPositions
    return OpenPositionsReturn

async def main():
    logger.info("Starting openPositionService!")
    response: SchemasOpenPositionReturn = await get_openPositions()
    return response

if __name__ == "__main__":
    try:
        response: SchemasOpenPositionReturn =asyncio.run(main())
        logger.info(json.dumps(response.openPositions, indent=4, default=str))
        logger.info(json.dumps(response.consolidatedOpenPositions, indent=4, default=str))
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