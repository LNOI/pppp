from typing import Iterable
import numpy as np
from src.utils.redis_utils import redis_mget
from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP

def vec_cache_query(post_ids:Iterable[int], vec_name:str) -> dict[int, np.ndarray]:
    cache_key_pattern = vec_name + ':*'
    cached_keys = [i.decode('utf-8') for i in RESOURCE_MAP['redis_conn'].keys(pattern=cache_key_pattern)]
    cached_post_ids = set([int(key_name.split(':')[-1]) for key_name in cached_keys])
    exist_ids = list(set(post_ids) & cached_post_ids)

    name_pattern = vec_name + ':%s'
    cache_keys = [name_pattern % post_id for post_id in exist_ids]
    cached_vecs = redis_mget(cache_keys, step_size=1000)
    exist_post_vector_map = {}
    for post_id, vec in zip(exist_ids, cached_vecs):
        if vec is not None:
            exist_post_vector_map[post_id] = np.frombuffer(vec).reshape(-1)
    return exist_post_vector_map

def cache_vector(post_vector_map:dict[int, np.ndarray], vec_name:str, expire_sec) -> None:
    name_pattern = vec_name + ':%s'
    cache_expire_sec = expire_sec # CONST_MAP.faiss_cache_expire_hour * 3600
    pipe = RESOURCE_MAP['redis_conn'].pipeline()
    for post_id, vector in post_vector_map.items():
        redis_keyname = name_pattern % (post_id)
        value = vector.tobytes()
        pipe.set(redis_keyname, value)
        pipe.expire(redis_keyname, cache_expire_sec)
    pipe.execute()