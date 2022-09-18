import numpy as np
import pymilvus
import math
from src.common.post_info_class import PostInfo
from src.common.get_style_history_vector import get_style_history_vector
from src.utils.faiss_utils import multi_search_index_condition, read_index_by_multiple_ids
from src.utils.redis_utils import get_viewed_post
from src.utils.query.user_history import get_latest_history
from src.const import const_map as CONST_MAP
from src.utils.decorator import log_func_time
import logging
logger = logging.getLogger('utils_logger')
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')

@log_func_time
def get_candidate_post_ids(user_id:int, posts_liked_vector:list[np.ndarray], buyable=True) -> list[int]:
    if buyable:
        index_name = 'buyable_faiss_index_v2'
    else:
        index_name = 'faiss_index_v2'
    
    avoid_ids = get_viewed_post(user_id)
    work_logger.info('User: %s. Start get recsys candidate: Avoid post and curating post %s' % (user_id, avoid_ids))
    candidate_post_ids = []
    control_size = CONST_MAP.recsys_candidate_control_size
    
    for i, user_vector in enumerate(posts_liked_vector):
        if control_size-i < 1:
            break
        faiss_search = multi_search_index([user_vector], 
                                                number_of_post=control_size-i, 
                                                col_name=index_name, 
                                                threshold=CONST_MAP.recsys_candidate_distance_threshold, 
                                                avoid_ids = avoid_ids)
        work_logger.info('Faiss near search result for %sth vector: %s' % (i, faiss_search))
        new_candidate_post_ids = [i for i in faiss_search if i not in candidate_post_ids and i != -1]
        work_logger.info('Faiss new candidate ids result for %sth vector: %s' % (i, new_candidate_post_ids))
        if len(new_candidate_post_ids) > 0:
            candidate_post_ids += new_candidate_post_ids
        if len(candidate_post_ids) >= CONST_MAP.recsys_candidate_number_limit:
            break

    work_logger.info('User: %s. Get recsys candidate: Candidate not in avoid post: %s' % (user_id, candidate_post_ids))
    return candidate_post_ids

@log_func_time
def recsys_post_raw(user_id:int) -> list[PostInfo]:
    buyable = True
    liked_id, disliked_id, liked_time_scores, disliked_time_scores = get_latest_history(user_id)
    posts_liked_vector, _ = get_style_history_vector(liked_id, [])
    candidate_post_ids = get_candidate_post_ids(user_id, posts_liked_vector, buyable)
    recsys_post_infos = [PostInfo(pid) for pid in candidate_post_ids]
    return recsys_post_infos

from src.recommendation.utils.recsys_scoring import get_user_vector_bytes
from src.common.post_info_class import add_post_score_info, add_post_recsys_score
from src.common.random_shuffle import random_post_info_shuffle
def new_recsys_today_index_source(user_id:int, limit=199):
    liked_id, disliked_id, liked_time_scores, disliked_time_scores = get_latest_history(user_id)
    posts_liked_vector, _ = get_style_history_vector(liked_id, [])
    if len(posts_liked_vector) < 1:
        similar_pids = []
    else:
        similar_pids = multi_search_index(posts_liked_vector, number_of_post=limit, col_name='style_v1')
    user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
    recsys_post_infos = [PostInfo(pid) for pid in similar_pids]
    add_post_score_info(recsys_post_infos)
    if user_vector is not None:
        add_post_recsys_score(recsys_post_infos, user_vector=user_vector)
    recsys_post_infos = random_post_info_shuffle(recsys_post_infos)
    return recsys_post_infos

def multi_search_index(vectors:list[np.ndarray], number_of_post:int, col_name:str, threshold:float=2, avoid_ids:list[int]=None):
    if CONST_MAP.milvus_fallback is True:
        return multi_search_index_condition(vectors, number_of_post, 'style_index_v1', threshold=threshold, avoid_ids=avoid_ids)
    else:
        return milvus_multi_search_index(vectors, number_of_post, col_name, threshold, avoid_ids)

def milvus_multi_search_index(vectors:list[np.ndarray], number_of_post:int, col_name:str, threshold:float=2, avoid_ids:list[int]=None):
    col = pymilvus.Collection(col_name)
    col.load()
    limit_per_request = math.ceil(number_of_post/len(vectors)) * 2
    vectors = [arr.tolist() for arr in vectors]
    search_res = col.search(vectors, 
                            anns_field='vec', 
                            limit=limit_per_request,
                            param={'metric':'L2', 'nprobe':500}
                            # expr='id not in %s' % str(avoid_ids)
                            )
    final_ids = []
    for single_request_res in search_res:
        for eid, distance in zip(single_request_res.ids, single_request_res.distances):
            if distance < threshold:
                final_ids.append(eid)
    # random.shuffle(final_ids)
    final_ids = list(dict.fromkeys(final_ids))
    return final_ids[:number_of_post]

def multi_post_similar_source(post_ids:list[int], number_of_post=100):
    input_vecs = list(read_index_by_multiple_ids(post_ids, 'faiss_index_v2').values())
    similar_ids = multi_search_index_condition(input_vecs, number_of_post, 'faiss_index_v2', threshold=2)
    return similar_ids