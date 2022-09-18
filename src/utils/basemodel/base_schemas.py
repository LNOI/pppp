from  pydantic import BaseModel,PydanticValueError,validator
from typing import Union, List, Any
from fastapi import status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')



class BaseUserSchema(BaseModel):
    user_id: int
    
    @validator("user_id")
    def v_userid(cls,v):
        if v < 1:
            v=-1
        return v
    
class BasePostSchema(BaseModel):
    post_id : int
    
    @validator('post_id')
    def val_post_id(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Post id must be bigger than 1.")
        return v

