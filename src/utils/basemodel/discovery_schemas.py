from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Literal, Optional, Any,Union
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from .base_schemas import BaseUserSchema
from .filter_schemas import FilterSchema
from fastapi.encoders import jsonable_encoder

    
class DiscoverySchema(BaseUserSchema): 
    no_watch_next: int
    filter: Union[FilterSchema,None]=None

    @validator('no_watch_next')
    def val_no_watch_next(cls, v):
        if v < 0 and v > 50 :
            v = 50
            # raise PydanticValueError(code=status.HTTP_400_BAD_REQUEST, msg_template="User ID must be bigger than 1.")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="User ID must be bigger than 1.")
        return v
    