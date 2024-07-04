# my_project/services/ledger_service.py
import argparse
import httpx
import time
import urllib.parse
import json
import asyncio
from typing import List, Optional
from pydantic import ValidationError
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.utils.utils import generate_api_signature
from krakenfx.services.schemas.account_data.OrderSchemas import (
    SchemasOrder,
    SchemasOrderDescription,
    SchemasOrdersResult,
    SchemasQueryOrdersResponse,
)
from krakenfx.utils.logger import setup_logging
logger = setup_logging()
settings = Settings()


@async_handle_errors
async def get_queryTrades(order_ids: List[str] = None, trades: bool = True, userref: Optional[int] = None, consolidate_taker: bool = False):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/QueryOrders"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    txid_str = ",".join(order_ids)
    logger.trace(f"Formatted txid string: {txid_str}")
    data = {
        "nonce": nonce,
        "txid": txid_str,
        "trades": True,
        "consolidate_taker": consolidate_taker
    }
    if userref is not None:
        data["userref"] = userref

    logger.trace(f"Data payload: {data}")

    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        logger.trace(f"Raw response content: {response.content}")
        response.raise_for_status()

        await check_response_errors(response.json())
        queryTradesResponse = SchemasQueryOrdersResponse(**response.json())
        await check_schemasResponse_empty(queryTradesResponse)

        return queryTradesResponse.result

    
async def main():
    logger.info("Query Ledger Service!")
    parser = argparse.ArgumentParser(description="Get a ledger entry information")
    parser.add_argument("-q", "--order_ids", type=str, help="Comma separated IDs of the Orders.", required=True)
    parser.add_argument("-t", "--trades", type=bool, help="Whether to include trades related to position in output", default=False, required=False)
    parser.add_argument("-u", "--userref", type=int, help="Restrict results to given user reference id", required=False)
    parser.add_argument("-c", "--consolidate_taker", type=bool, help="Whether to consolidate trades by individual taker trades", default=True, required=False)
    args = parser.parse_args()
    order_ids = args.order_ids.split(',')

    response = await get_queryTrades(order_ids, args.trades, args.userref, args.consolidate_taker)
    return response

if __name__ == "__main__":
    try:
        response = asyncio.run(main())
        logger.info(f"Raw response: {response}")
        response_dict = {k: v.model_dump() for k, v in response.items()}
        logger.info(json.dumps(response_dict, indent=4, default=str))

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