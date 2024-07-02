# krakenfx/services/open_order_service.py
import httpx
import time
import urllib.parse
import json
import asyncio
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.logger import setup_logging
from krakenfx.api.schemas.openOrderSchemas import (
    SchemasOpenOrdersResponse,
    SchemasOpenOrdersResult
)

logger = setup_logging()

@handle_errors
async def get_openOrders():
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/OpenOrders"
    url = Settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce
    }
    headers = {
        "API-Key": Settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, Settings.KRAKEN_API_SECRET)
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()
        
        await check_response_errors(response.json())
        openOrdersResponse = SchemasOpenOrdersResponse(**response.json())
        await check_schemasResponse_empty(openOrdersResponse)
        return openOrdersResponse
        
async def main():
    logger.info("Starting openOrderService!")
    response: SchemasOpenOrdersResponse = await get_openOrders()
    return response

if __name__ == "__main__":
    try:
        logger.info(asyncio.run(main()).model_dump())
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
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)