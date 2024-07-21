import argparse
import asyncio
import json
import logging
import time
import urllib.parse
from typing import List, Optional

import httpx
from pydantic import ValidationError

from krakenfx.di.app_container import AppContainer
from krakenfx.services.account_data.schemas.OrderSchemas import (
    SchemasQueryOrdersResponse,
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
async def get_queryTrades(
    settings: Settings,
    order_ids: List[str] = None,
    trades: bool = True,
    userref: Optional[int] = None,
    consolidate_taker: bool = False,
):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/QueryOrders"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    txid_str = ",".join(order_ids)
    data = {
        "nonce": nonce,
        "txid": txid_str,
        "trades": True,
        "consolidate_taker": consolidate_taker,
    }
    if userref is not None:
        data["userref"] = userref

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
        queryTradesResponse = SchemasQueryOrdersResponse(**response.json())
        await check_schemasResponse_empty(queryTradesResponse)

        return queryTradesResponse.result


async def main(settings: Settings, logger: logging.Logger):
    logger.info("Query Ledger Service!")
    parser = argparse.ArgumentParser(description="Get a ledger entry information")
    parser.add_argument(
        "-q",
        "--order_ids",
        type=str,
        help="Comma separated IDs of the Orders.",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--trades",
        type=bool,
        help="Whether to include trades related to position in output",
        default=False,
        required=False,
    )
    parser.add_argument(
        "-u",
        "--userref",
        type=int,
        help="Restrict results to given user reference id",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--consolidate_taker",
        type=bool,
        help="Whether to consolidate trades by individual taker trades",
        default=True,
        required=False,
    )
    args = parser.parse_args()
    order_ids = args.order_ids.split(",")

    response = await get_queryTrades(
        settings, order_ids, args.trades, args.userref, args.consolidate_taker
    )
    return response


if __name__ == "__main__":
    try:
        logger = AppContainer().logger_container().logger()
        settings = AppContainer().config_container().config()
        response = asyncio.run(main(settings, logger))
        logger.info(f"Raw response: {response}")
        response_dict = {k: v.model_dump() for k, v in response.items()}
        logger.info(json.dumps(response_dict, indent=4, default=str))

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
