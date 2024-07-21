import json
from typing import TypeVar

from pydantic import BaseModel

from krakenfx.di.logger_container import LoggerContainer
from krakenfx.utils.errors import (
    KrakenFetchResponseException,
    KrakenInvalidAPIKeyException,
    KrakenInvalidResponseStructureException,
    KrakenNoItemsReturnedException,
    async_handle_errors,
)

logger = LoggerContainer().logger()

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


@async_handle_errors
async def check_response_errors(response):
    if response["error"] and len(response["error"]) > 0:
        logger.trace(json.dumps(f"L> Response contain errors: {response['error']}"))
        if "EAPI:Invalid key" in response["error"]:
            raise KrakenInvalidAPIKeyException(
                f"KrakenInvalidAPIKeyException: {response['error']}"
            )
        raise KrakenFetchResponseException(
            f"KrakenFetchResponseException: {json.dumps(response['error'], indent=4)}"
        )
    elif "error" not in response or "result" not in response:
        raise KrakenInvalidResponseStructureException(
            f"KrakenInvalidResponseStructureException: 'error' or 'result' field missing in response: {response.json()})"
        )
    else:
        logger.info("API ResponseOK, No errors found in response.")


@async_handle_errors
async def check_schemasResponse_empty(
    response: T, field: str = None
):  # field expect ['open','closed','trades', 'ledger']
    if field is None:
        if hasattr(response, "result"):
            response_field = response.result
            if (isinstance(response_field, dict) and len(response_field) == 0) or (
                hasattr(response_field, "model_dump")
                and len(response_field.model_dump()) == 0
            ):
                logger.debug(
                    "L_> Variable: check_schemasResponse_empty().response:\n{}".format(
                        json.dumps(response.model_dump(), indent=4)
                    )
                )
                raise KrakenNoItemsReturnedException(
                    "KrakenNoItemsReturnedException: No items found! Return: 0"
                )
        else:
            raise KrakenInvalidResponseStructureException(
                "Invalid response, missing field 'result'"
            )
    elif hasattr(response.result, field):
        response_field = getattr(response.result, field)
        if len(response_field) == 0:
            logger.debug(
                "L_> Variable: check_schemasResponse_empty().response:\n{}".format(
                    json.dumps(response.model_dump(), indent=4)
                )
            )
            raise KrakenNoItemsReturnedException(
                f"KrakenNoItemsReturnedException: No items found! Order: {len(response_field)}"
            )
    else:
        raise KrakenInvalidResponseStructureException(
            f"Invalid response, missing field {field}"
        )


__all__ = ["check_response_errors", "check_schemasResponse_empty"]
