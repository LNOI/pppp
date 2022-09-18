from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from .base_schemas import BaseUserSchema

class PersonalizeNotiSchema(BaseUserSchema):
    pass

class FollowingNotiSchema(BaseModel):
    user_ids: list[int]
    
    @validator("user_ids")
    def val_user_ids(cls,v):
        for i in v:
            if i < 1:
                 return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Post id must be bigger than 1.")
        return v
             