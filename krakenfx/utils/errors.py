class TimeoutError(Exception):
    def __init__(self, message=f"TimeoutError: Timeout error: {Exception}"):
        self.message = message
        super().__init__(self.message)

class RuntimeError(Exception):
    def __init__(self, message=f"RuntimeError: Runtime error: {Exception}"):
        self.message = message
        super().__init__(self.message)

class ConnectionError(Exception):
    def __init__(self, message=f"ConnectionError: Connection error: {Exception}"):
        self.message = message
        super().__init__(self.message)

class InvalidAPIKeyException(Exception):
    def __init__(self, message=f"InvalidAPIKeyException: {Exception}"):
        self.message = message
        super().__init__(self.message)

class NoOrdersException(Exception):
    def __init__(self, message=f"NoOrdersException: {Exception}"):
        self.message = message
        super().__init__(self.message)

class FetchResponseException(Exception):
    def __init__(self, message=f"FetchResponseException {Exception}"):
        self.message = message
        super().__init__(self.message)

class ValueError(Exception):
    def __init__(self, message=f"ValueError: {Exception}"):
        self.message = message
        super().__init__(self.message)

class InvalidResponseStructureException(Exception):
    def __init__(self, message=f"InvalidResponseStructureException: {Exception}"):
        self.message = message
        super().__init__(self.message)

class ExceptionInvalidOrderStatus(Exception):
    def __init__(self,message=f"Exception: {Exception}"):
        self.message = message
        super().__init__(self.message)

class Exception(Exception):
    def __init__(self,message=f"Exception: {Exception}"):
        self.message = message
        super().__init__(self.message)


def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise TimeoutError(e)
        except RuntimeError as e:
            raise RuntimeError(e)
        except ConnectionError as e:
            raise ConnectionError(e)
        except NoOrdersException as e:
            raise NoOrdersException(e)
        except FetchResponseException as e:
            raise FetchResponseException(e)
        except InvalidAPIKeyException as e:
            raise InvalidAPIKeyException(e)
        except InvalidResponseStructureException as e:
            raise InvalidResponseStructureException(e)
        except ExceptionInvalidOrderStatus as e:
            raise ExceptionInvalidOrderStatus(e)
        except ValueError as e:
            raise ValueError(e)
        except Exception as e:
            raise Exception(e)
    return wrapper