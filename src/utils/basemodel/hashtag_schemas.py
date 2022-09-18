from  pydantic import BaseModel,PydanticValueError,validator
from typing import Union, List, Any
from fastapi import status
from fastapi.responses import JSONResponse
import logging


class HashtagSuggestionItemSchema(BaseModel):
    hashtag_id : int
    total_post : int

class HashtagSuggestionSourceSchema(BaseModel):
    text : str
    hashtags : list[HashtagSuggestionItemSchema]