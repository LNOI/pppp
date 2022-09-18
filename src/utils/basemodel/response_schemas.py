import json

from typing import List, Optional, Any
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import  Response


def create_response(status: int, content: Any, isJsonable=False):
    if isJsonable:
        content = jsonable_encoder(content)
    content=json.dumps(content)
    return Response(status_code=status, content=content, media_type="application/json")
