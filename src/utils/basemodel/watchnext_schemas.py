from unittest.mock import Base
from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any,Union
from fastapi import status
from .base_schemas import BaseUserSchema
from .filter_schemas import FilterSchema
from fastapi.responses import JSONResponse


class WatchnextSchema(BaseUserSchema):
    no_watch_next : int
    filter : Union[FilterSchema,None]=None
    
    @validator('no_watch_next')
    def val_no_watch_next(cls, v):
        if v < 0 and v > 50 :
            v = 50
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="User ID must be bigger than 1.")
        return v
