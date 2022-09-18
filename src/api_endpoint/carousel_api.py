import numpy as np
from src.api_endpoint.add_api import short_api_log
from src.const.global_map import RESOURCE_MAP
from src.utils.query.user_history import get_latest_history
from src.recommendation.utils.recsys_scoring import get_user_vector_bytes, get_new_post_scores
from src.common.get_style_history_vector import get_embed_vector
from src.utils.basemodel.response_schemas import create_response
from src.utils.basemodel import carousel_schemas as schemas
from fastapi.encoders import jsonable_encoder
app = RESOURCE_MAP['fastapi_app']

from src.const import const_map as CONST_MAP


@app.post('/user_history')
async def get_user_history(input_map:  schemas.SimpleUser):
    user_id = input_map.user_id
    liked_id, disliked_id, _, _ = get_latest_history(user_id)
    res = {
        'liked_posts': liked_id,
        'disliked_posts': disliked_id
    }
    return create_response(status=200, content=res)

@app.post('/user_vector')
async def get_user_vector(input_map: schemas.SimpleUser):
    user_id = input_map.user_id
    user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
    res = {'user_vector': user_vector.tolist()}
    return create_response(status=200, content=res)

@app.post('/post_vector')
async def get_post_vector(input_map: schemas.SimplePost):
    post_id = input_map.post_id
    post_vector_map = get_embed_vector([post_id])
    res = {
        'post_vector':post_vector_map[post_id].tolist()
    }
    return create_response(status=200, content=res)

@app.post('/user_post_scoring')
async def get_user_post_scoring(input_map: schemas.UserPost): 
    user_id = input_map.user_id
    user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
    post_id = input_map.post_id
    post_vector_map = get_embed_vector([post_id])
    post_vector = post_vector_map[post_id]
    score_map = get_new_post_scores([(post_id, post_vector)], user_vector)
    res = {
        'score':score_map[post_id]
    }
    return create_response(status=200, content=res)