import httpx
import time
import urllib.parse
import json
import asyncio
from pydantic import ValidationError
from krakenfx.utils.errors import *
from krakenfx.utils.validations import *
from krakenfx.core.config import Settings
from krakenfx.services.spot_market_data.schemas.recentTradesSchemas import (
    SchemasRecentTradesResponse,
)
from krakenfx.utils.utils import generate_api_signature
from krakenfx.utils.logger import setup_logging

logger = setup_logging()
settings = Settings()

@async_handle_errors
async def get_recent_trades(pair: str, since: str = None):
    nonce = int(time.time() * 1000)
    urlpath = "/0/public/Trades"
    url = settings.KRAKEN_API_URL.unicode_string().rstrip('/') + urlpath
    data = {
        "nonce": nonce,
        "pair": pair,
    }
    if since:
        data["since"] = since
    
    headers = {
        "API-Key": settings.KRAKEN_API_KEY,
        "API-Sign": generate_api_signature(urlpath, data, settings.KRAKEN_API_SECRET),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=urllib.parse.urlencode(data))
        response.raise_for_status()

        await check_response_errors(response.json())
        trades_response = SchemasRecentTradesResponse.from_response(response.json())
        await check_schemasResponse_empty(trades_response)
        asset_pair_trades = trades_response.result.get(pair, [])
        return asset_pair_trades

async def main():
    logger.info("Get Recent Trades from Kraken server!")
    pair = "XXBTZUSD"
    response = await get_recent_trades(pair)
    return response

if __name__ == "__main__":
    try:
        response = asyncio.run(main())
        logger.info(json.dumps([trade.model_dump() for trade in response], indent=4, default=str))

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
        error = json.dumps(e.errors(), indent=4)
        logger.error(error)
    except ValueError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
