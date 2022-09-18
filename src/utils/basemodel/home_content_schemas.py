from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Optional, Any,Literal
from fastapi import File, status
from fastapi.responses import JSONResponse
from .base_schemas import BaseUserSchema,BasePostSchema


class HomeContentInputSchema(BaseUserSchema):
    component_index: Optional[int]=None



