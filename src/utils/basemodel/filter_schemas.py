from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Literal, Optional, Any,Union
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from .base_schemas import BaseUserSchema
from fastapi.encoders import jsonable_encoder

class FilterSchema(BaseModel):
    category :Optional[list[int]]=[]
    size : Optional[list[int]]=[]
    condition : Optional[list[int]]=[]
    price :Optional[list[int]]=[]
    sex : Optional[list[int]]=[]