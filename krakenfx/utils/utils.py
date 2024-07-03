# krakenfx/core/utils.py
import urllib.parse
import hashlib
import hmac
import base64
import json
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

async def truncated_output(json_data: dict, nbs_lines = int) -> dict:
    json_lines = json_data.split('\n')
    if len(json_lines) > nbs_lines:
        json_lines = json_lines[:nbs_lines]
        json_lines.append("... [truncated]")
    truncated_data = '\n'.join(json_lines)
    
    return truncated_data


__all__ = ['generate_api_signature', 'object_as_dict', 'truncated_output']