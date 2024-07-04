import asyncio
import json
from krakenfx.utils.errors import *
from krakenfx.api.schemas import *
from krakenfx.utils.errors import *
from krakenfx.utils.logger import setup_logging
from typing import List, TypeVar
from pydantic import BaseModel

logger = setup_logging()

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

@async_handle_errors
async def check_response_errors(response):
    if response['error'] and len(response['error']) > 0:
        logger.trace(json.dumps(f"L> Response contain errors: {response['error']}"))
        if "EAPI:Invalid key" in response['error']:
            raise InvalidAPIKeyException(f"InvalidAPIKeyException: {response['error']}")
        raise FetchResponseException(f"FetchResponseException: {json.dumps(response['error'], indent=4)}")
    elif 'error' not in response or 'result' not in response:
        raise InvalidResponseStructureException(f"InvalidResponseStructureException: 'error' or 'result' field missing in response: response.json())")
    else:
        logger.info("API ResponseOK, No errors found in response.")

@async_handle_errors
async def check_schemasResponse_empty(response: T, field: str = None): # field expect ['open','closed','trades', 'ledger']
    if field is None:
        if hasattr(response, "result"):
            response_field = getattr(response, "result")
            if (isinstance(response_field, dict) and len(response_field) == 0) or (hasattr(response_field, 'model_dump') and len(response_field.model_dump()) == 0):
                logger.debug("L_> Variable: check_schemasResponse_empty().response:\n{}".format(json.dumps(response.model_dump(), indent=4)))
                raise NoOrdersException("NoOrdersException: No items found! Order: 0")
        else:
            raise InvalidResponseStructureException("Invalid response, missing field 'result'")
    elif hasattr(response.result, field):
        response_field = getattr(response.result, field)
        if len(response_field) == 0:
            logger.debug("L_> Variable: check_schemasResponse_empty().response:\n{}".format(json.dumps(response.model_dump(), indent=4)))
            raise NoOrdersException(f"NoOrdersException: No items found! Order: {len(response_field)}")
    else:
            raise InvalidResponseStructureException(f"Invalid response, missing field {field}")

__all__ = ['check_response_errors', 'check_schemasResponse_empty']
