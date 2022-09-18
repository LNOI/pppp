from unittest.mock import Base
from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any
from fastapi import status
from .base_schemas import BasePostSchema, BaseUserSchema
from fastapi.responses import JSONResponse

class ModelId(BaseModel):
    model_id: int
    
    @validator("model_id")
    def val_model_id(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Model id must be bigger than 1.")
        return v 

class VFDiscoverySchema(BaseUserSchema,ModelId):
   pass
    
    
class VFPostSchema(BaseUserSchema, BasePostSchema,ModelId):
    pass
    