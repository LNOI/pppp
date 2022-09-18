import numpy as np
from collections import defaultdict
from src.common.cache_vector import cache_vector, vec_cache_query
from src.utils.faiss_utils import read_index_by_multiple_ids
from src.utils.decorator import log_func_time
from src.utils.exception import FaissIndexError
from src.const import const_map as CONST_MAP
import pymilvus
import logging

work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')

# Actually, style history vector from faiss index style_index_v1 combine both meta vec (dim 21) and style vec (dim 11)
# So style history vec (dim 32) is different from style shop vec (dim 11) (contain only the dim 11 style vec)


@log_func_time
def get_style_history_vector(liked_id: list[int], disliked_id: list[int]) -> tuple[list[np.ndarray], list[np.ndarray]]:
    total_vector = get_embed_vector(liked_id + disliked_id)
    posts_liked_vector = [total_vector[pid] for pid in liked_id]
    posts_disliked_vector = [total_vector[pid] for pid in disliked_id]
    return posts_liked_vector, posts_disliked_vector


def get_embed_vector(post_ids: list[int]) -> dict[int, np.ndarray]:
    exist_post_vector_map = vec_cache_query(post_ids, 'style:vec:v2')
    exist_post_vector_map = {pid: exist_post_vector_map[pid].reshape(-1) for pid in exist_post_vector_map}
    new_ids = list(set(post_ids) - set(exist_post_vector_map.keys()))
    new_post_vector_map = direct_get_style_vector(new_ids)
    cache_vector(new_post_vector_map, 'style:vec:v2', 3600)
    return defaultdict(lambda: np.ones((CONST_MAP.style_post_size+21,)), {**exist_post_vector_map, **new_post_vector_map})


def direct_get_style_vector(post_ids: list[int]) -> dict[int, np.ndarray]:
    if CONST_MAP.milvus_fallback is True:
        if len(post_ids) < 1:
            return {}
        try:
            style_vec_map = read_index_by_multiple_ids(post_ids, 'style_index_v1')
        except FaissIndexError as e:
            style_vec_map = {}  # {pid: np.ones((CONST_MAP.style_post_size+21,)) for pid in post_ids}
        res = {pid: style_vec_map[pid] for pid in post_ids if pid in style_vec_map}
        return res

    else:
        col = pymilvus.Collection('style_v1')
        col.load()
        query_res = col.query(expr='id in %s' % str(post_ids), output_fields=['vec'])
        vec_map = {
            item['id']: np.array(item['vec']).reshape(-1)
            for item in query_res
        }
        return vec_map
