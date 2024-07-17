# krakenfx/services/ledger_service.py
import argparse
import asyncio
import json
import time
import urllib.parse
from typing import List

import httpx
from pydantic import ValidationError

from krakenfx.core.config import Settings
from krakenfx.services.account_data.schemas.tradehistorySchemas import (
    SchemasQueryTradesResponse,
)
from krakenfx.utils.errors import (
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

trade_id = ()


@async_handle_errors
async def get_queryTrades(trade_id: List[str] = trade_id):
    nonce = int(time.time() * 1000)
    urlpath = "/0/private/QueryTrades"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip("/") + urlpath
    data = {"nonce": nonce, "txid": trade_id, "trades": True}
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
        queryTradesResponse = SchemasQueryTradesResponse(**response.json())
        await check_schemasResponse_empty(queryTradesResponse)

        return queryTradesResponse.result


async def main():
    logger.info("Query Ledger Service!")
    parser = argparse.ArgumentParser(description="Get a ledger entry information")
    parser.add_argument(
        "-q",
        "--trade_id",
        type=str,
        help="Comma separated ID of the Trades.",
        required=True,
    )
    args = parser.parse_args()

    response = await get_queryTrades(args.trade_id)
    return response


if __name__ == "__main__":
    try:
        response = asyncio.run(main())
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
    except KrakenNoOrdersException as e:
        logger.error(e)
    except ValidationError as e:
        error = json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
