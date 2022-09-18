from  pydantic import BaseModel,PydanticValueError,validator
from typing import Optional, Union, List, Any
from fastapi import status
from fastapi.responses import JSONResponse
import logging


class SolrSearchHashtagSchema(BaseModel):
    name : str
    post_ids : list[int]
    total_view : int
    total_post : int


class SolrSearchSchema(BaseModel):
    hashtag : Optional[SolrSearchHashtagSchema]
    post : list[int]
    account : list[int]