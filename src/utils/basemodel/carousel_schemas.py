from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any
from fastapi import status
from fastapi.responses import JSONResponse

from src.utils.basemodel.base_schemas import BasePostSchema, BaseUserSchema

class SimpleUser(BaseUserSchema):
    pass
    
    
class SimplePost(BasePostSchema):
    pass
    
    
class UserPost(BaseUserSchema,BasePostSchema):
    pass