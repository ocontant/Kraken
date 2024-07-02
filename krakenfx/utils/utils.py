# krakenfx/core/utils.py
import urllib.parse
import hashlib
import hmac
import base64
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
import pdb

def generate_api_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

def pydantic_to_sqlalchemy_model(schema):
    """
    Iterates through pydantic schema and parses nested schemas
    to a dictionary containing SQLAlchemy models.
    Only works if nested schemas have specified the Meta.orm_model.
    """
    parsed_schema = schema.model_dump()  # Use dict() method instead of dict() to get model's dictionary representation
    pdb.set_trace()
    for key, value in parsed_schema.items():
        try:
            if isinstance(value, list) and len(value) and is_pydantic(value[0]):
                pdb.set_trace()
                parsed_schema[key] = [
                    item.Meta.orm_model(**pydantic_to_sqlalchemy_model(item))
                    for item in value
                ]
            elif is_pydantic(value):
                pdb.set_trace()
                parsed_schema[key] = value.Meta.orm_model(
                    **pydantic_to_sqlalchemy_model(value)
                )
        except AttributeError:
            raise AttributeError(
                f"Found nested Pydantic model in {schema.__class__} but Meta.orm_model was not specified."
            )
    return parsed_schema

def is_pydantic(obj: object) -> bool:
    """Checks whether an object is a Pydantic model."""
    return isinstance(obj, BaseModel)


__all__ = ['generate_api_signature', 'object_as_dict', 'is_pydantic', 'pydantic_to_sqlalchemy_model']