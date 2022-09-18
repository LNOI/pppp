from optparse import Option
from numpy import fromregex
from pydantic import BaseModel, validator, PydanticValueError, AnyUrl, Field
from typing import List, Union, Any,Literal, Optional
from fastapi import status
from fastapi.responses import JSONResponse
from .base_schemas import BasePostSchema,BaseUserSchema
from .filter_schemas import FilterSchema
class EncodingSchema(BaseModel):
    item: list[int]
    
    @validator('item')
    def val_item(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Item must be bigger than 1.")
        return v
class SimpleUserSchema(BaseUserSchema):
    pass
    
class PopularKeywordSchema(BaseModel):
    number_of_keyword: int
    
    @validator('number_of_keyword')
    def val_n_o_k(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="number_of_keyword  must be bigger than 1.")
        return v
        

class PopularHashtagSchema(BaseModel):
    number_of_hashtag: int
    
    @validator('number_of_hashtag')
    def val_n_o_h(cls,v):
        if v < 0 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="number_of_hashtag  must be bigger than 0.")
        return v
    

class HashtagSuggestionSchema(BaseUserSchema):
    number_of_hashtag: int

    @validator('number_of_hashtag')
    def val_hashtag(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Number of hashtag must be bigger than 1.")
        return v


class DeleleFaissSchema(BaseModel):
    post_ids: list[int]
    save_after_delete: bool
    
    @validator("post_ids")
    def val_post_ids(cls,v):
        for i in v:
            if i < v:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Post id must be bigger than 1.")
        return v
    

class ImageSimilaritySchema(BasePostSchema):
    number_of_post: int
     
    @validator('number_of_post')
    def val_n_o_p(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="number_of_post must be bigger than 1.")
        return v 
    
    
class ChatSuggestionSchema(BaseUserSchema,BasePostSchema):
    pass
    
    

class LeaderboardSchema(BaseUserSchema):
    pass


class PostSuggestionSchema(BaseUserSchema):
    reference_post_ids: list[int]
    source_name: str
    pool_size: int

    @validator("reference_post_ids")
    def val_rp_ids(cls,v):
        for i in v:
            if i < v:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Post id must be bigger than 1.")
        return v
    
    @validator('source_name')
    def val_s_n(cls,v):
        for i in v:
            if i not in ['popular', 'popular_business', 'featured', 'newpost', 'recsys', 'following', 'new_2hand']:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Source name must be in Range")
        return v
    
    @validator('pool_size')
    def val_p_s(cls,v):
        if v < 1 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="pool_size must be bigger than 1.")
        return v


class PostSuggestUserSchema(BaseUserSchema,BasePostSchema):
    pass
    

    
class WatchnextSchema(BaseUserSchema):
    keyword : str
    filter : Union[FilterSchema,None]=None
    
    
class KeywordSuggestionSchema(BaseUserSchema):
    number_of_keyword: Optional[int]

class ItemCommisionFeeSchema(BasePostSchema):
    price_after_sales: int
    
    
    
    


    
    