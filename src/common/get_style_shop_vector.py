import numpy as np
from collections import defaultdict
from src.common.cache_vector import cache_vector, vec_cache_query
from src.utils.db_utils import execute_raw_query
from src.const import const_map as CONST_MAP
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')

def get_shop_embed_vector(shop_ids:list[int]) -> dict[int, np.ndarray]:
    exist_shop_vector_map = vec_cache_query(shop_ids, 'style:shop:vec:v1')
    exist_shop_vector_map = {pid:exist_shop_vector_map[pid].reshape(-1) for pid in exist_shop_vector_map}
    new_ids = list(set(shop_ids) - set(exist_shop_vector_map.keys()))
    new_shop_vector_map = direct_get_shop_embed_vector(new_ids)
    cache_vector(new_shop_vector_map, 'style:shop:vec:v1', 3600)
    return defaultdict(lambda: np.ones((CONST_MAP.embed_post_size,)),{**exist_shop_vector_map, **new_shop_vector_map})

def direct_get_shop_embed_vector(shop_ids:list[int]) -> dict[int, np.ndarray]:
    if len(shop_ids) < 1:
        return {}
    query = '''select hp.hashtag_id, p.user_id, count(0) as post_count from hashtag_post hp left join post p on hp.post_id = p.id 
    where p.user_id in :shop_ids
    and hp.hashtag_id in (77,93,55,81,399,391,228,266,73,381,270)
    group by hp.hashtag_id, p.user_id'''
    res = execute_raw_query(query, shop_ids=tuple(shop_ids))
    shop_map = {sid:{hp_id:0 for hp_id in [77,93,55,81,399,391,228,266,73,381,270]} for sid in shop_ids}
    for hashtag, uid, post_count in res:
        shop_map[uid][hashtag] = post_count
    return {sid:get_single_shop_style_vec(shop_map[sid]) for sid in shop_ids}

def get_single_shop_style_vec(hashtag_map:dict[int,int]) -> np.ndarray:
    num_style = 11
    res_vec = np.array([0.0] * num_style).reshape(-1)
    for hashtag in hashtag_map:
        res_vec[style_id2class(hashtag)] = hashtag_map[hashtag]
    res_vec = res_vec + 1e-1
    res_vec = res_vec/sum(res_vec)
    res_vec = -2*np.log(res_vec)
    return res_vec

def style_id2class(style_id: int)-> int:
    style_index_map = {
        55: 0, 
        228: 1, 
        391: 2, 
        77: 3, 
        381: 4, 
        266: 5, 
        270: 6, 
        73: 7, 
        81: 8, 
        399: 9, 
        93: 10
    }
    if style_id in style_index_map:
        return style_index_map[style_id]
    raise Exception(f"Unaccepted style index: {style_id}")