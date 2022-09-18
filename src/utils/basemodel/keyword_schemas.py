from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from .base_schemas import BaseUserSchema


class KeywordSuggestionItem(BaseModel):
    text : str
    keywords : list[str]