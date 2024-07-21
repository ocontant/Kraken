# krakenfx/services/tradebalance_service.py
import asyncio
import json
import logging
import time
import urllib.parse

import httpx
from pydantic import ValidationError

from krakenfx.di.app_container import AppContainer
from krakenfx.services.account_data.schemas.tradebalanceSchemas import (
    SchemasTradeBalance,
    SchemasTradeBalanceResponse,
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
async def get_tradeBalance(settings: Settings):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/TradeBalance"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {"nonce": nonce, "asset": "zusd"}
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, headers=headers, content=urllib.parse.urlencode(data)
        )
        response.raise_for_status()

        await check_response_errors(response.json())
        tradeBalanceResponse = SchemasTradeBalanceResponse(**response.json())
        await check_schemasResponse_empty(tradeBalanceResponse)
        tradeBalance: SchemasTradeBalance = tradeBalanceResponse.result

        return tradeBalance


async def main(settings: Settings, logger: logging.Logger):
    logger.info("Starting closedOrderService!")
    response: SchemasTradeBalance = await get_tradeBalance(settings)
    return response


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        logger.info(asyncio.run(main(settings, logger)))
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
