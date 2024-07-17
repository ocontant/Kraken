import asyncio
import json
import time
import urllib.parse

import httpx
from pydantic import ValidationError

from krakenfx.core.config import Settings
from krakenfx.services.account_data.schemas.OrderSchemas import (
    SchemasOrdersResponse,
    SchemasOrdersResult,
)
from krakenfx.utils.errors import (
    KrakenExceptionInvalidOrderStatus,
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoOrdersException,
    async_handle_errors,
)
from krakenfx.utils.logger import setup_logging
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.validations import (
    check_response_errors,
    check_schemasResponse_empty,
)

logger = setup_logging()
settings = Settings()


@async_handle_errors
async def get_Orders(order_status=str):
    nonce = int(time.time() * 1000)
    match order_status:
        case "open":
            urlpath = "/0/private/OpenOrders"
        case "closed":
            urlpath = "/0/private/ClosedOrders"
        case _:
            raise KrakenExceptionInvalidOrderStatus(
                f"Options: open|closed. Value received: {order_status}"
            )

    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {"nonce": nonce}
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
        OrdersResponse = SchemasOrdersResponse(**response.json())
        await check_schemasResponse_empty(OrdersResponse, order_status)
        Orders: SchemasOrdersResult = getattr(OrdersResponse.result, order_status)
        return Orders


async def main(order_status=str):
    logger.info("Starting closedOrderService!")
    response: SchemasOrdersResult = await get_Orders(order_status)
    return response


if __name__ == "__main__":
    try:
        logger.info(asyncio.run(main("open")))
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
