class KrakenInvalidAPIKeyException(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"KrakenInvalidAPIKeyException: {Exception}"):
        self.message = message
        super().__init__(self.message)


class KrakenFetchResponseException(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"KrakenFetchResponseException {Exception}"):
        self.message = message
        super().__init__(self.message)


class KrakenValueError(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"ValueError: {Exception}"):
        self.message = message
        super().__init__(self.message)


class KrakenInvalidResponseStructureException(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"KrakenInvalidResponseStructureException: {Exception}"):
        self.message = message
        super().__init__(self.message)


class KrakenExceptionInvalidOrderStatus(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"Exception: {Exception}"):
        self.message = message
        super().__init__(self.message)


class KrakenNoOrdersException(Exception):
    """Utilities for handling errors in KrakenFX."""

    def __init__(self, message=f"KrakenNoOrdersException: {Exception}"):
        self.message = message
        super().__init__(self.message)


def async_handle_errors(func):
    """
    Decorator to catch exceptions raised by the wrapped asynchronous function.
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise TimeoutError(e) from e
        except RuntimeError as e:
            raise RuntimeError(e) from e
        except ConnectionError as e:
            raise ConnectionError(e) from e
        except KrakenNoOrdersException as e:
            raise KrakenNoOrdersException(e) from e
        except KrakenFetchResponseException as e:
            raise KrakenFetchResponseException(e) from e
        except KrakenInvalidAPIKeyException as e:
            raise KrakenInvalidAPIKeyException(e) from e
        except KrakenInvalidResponseStructureException as e:
            raise KrakenInvalidResponseStructureException(e) from e
        except KrakenExceptionInvalidOrderStatus as e:
            raise KrakenExceptionInvalidOrderStatus(e) from e
        except ValueError as e:
            raise ValueError(e) from e
        except Exception as e:
            raise Exception(f"General exception occurred: {e}") from e

    return wrapper


def handle_errors(func):
    """Decorator to catch exceptions raised by the wrapped function."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TimeoutError as e:
            raise TimeoutError(e) from e
        except RuntimeError as e:
            raise RuntimeError(e) from e
        except ConnectionError as e:
            raise ConnectionError(e) from e
        except KrakenNoOrdersException as e:
            raise KrakenNoOrdersException(e) from e
        except KrakenFetchResponseException as e:
            raise KrakenFetchResponseException(e) from e
        except KrakenInvalidAPIKeyException as e:
            raise KrakenInvalidAPIKeyException(e) from e
        except KrakenInvalidResponseStructureException as e:
            raise KrakenInvalidResponseStructureException(e) from e
        except KrakenExceptionInvalidOrderStatus as e:
            raise KrakenExceptionInvalidOrderStatus(e) from e
        except ValueError as e:
            raise ValueError(e) from e
        except Exception as e:
            raise BaseException(f"An unexpected error occurred: {e}") from e

    return wrapper
