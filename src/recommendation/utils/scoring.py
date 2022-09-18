import numpy as np
from src.common.post_info_class import add_post_score_info_to_source_map, PostInfo
from src.utils.decorator import log_func_time
from src.common.random_shuffle import result_prob_random_change
from src.recommendation.utils.recsys_scoring import get_user_vector_bytes
from src.common.post_info_class import add_post_recsys_score
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')

@log_func_time
def get_final_score(user_id:int, source_candidate_map: dict[str, list[PostInfo]], require_post_number:int=10) -> dict[str, list[PostInfo]]:
    try:
        source_candidate_map = add_score_boost(user_id, source_candidate_map, require_post_number)
    except Exception as e:
        err_logger.error('DB score boost failed: %s' % e, exc_info=True)
    try:
        source_candidate_map = add_recsys_similar_score(user_id, source_candidate_map)
    except Exception as e:
        err_logger.error('Recsys similar score boost failed: %s' % e, exc_info=True)
    return source_candidate_map

# only for those source not using sql to get post scoring
def add_score_boost(user_id:int, source_candidate_map: dict[str, list[PostInfo]], require_post_number:int=10) -> dict[str, list[PostInfo]]:
    try:
        if 'popular' in source_candidate_map:
            for post_info in source_candidate_map['popular']:
                post_info.post_score_info['raw_score'] = post_info.source_specific_info['popular_score']
        if 'popular_business' in source_candidate_map:
            for post_info in source_candidate_map['popular_business']:
                post_info.post_score_info['raw_score'] = post_info.source_specific_info['popular_score']
        add_post_score_info_to_source_map(source_candidate_map)
        source_candidate_map = random_post_selection(source_candidate_map, 50 if require_post_number < 50 else require_post_number)
    except Exception as e:
        deviation_logger.info('User: %s. post scoring error %s: %s' % (user_id, e, source_candidate_map), exc_info=True)
    return source_candidate_map

@log_func_time
def add_recsys_similar_score(user_id:int, source_candidate_map: dict[str, list[PostInfo]]) -> dict[str, list[PostInfo]]:
    try:
        source_list = ['shop', 'post', 'popular_business', 'popular', 'featured', 'recsys', 'following', 'preference', 'newpost']
        post_infos = []
        for source in source_list:
            if source in source_candidate_map:
                post_infos += source_candidate_map[source]
        user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
        add_post_recsys_score(post_infos, user_vector)
    except Exception as e:
        deviation_logger.info('User: %s. recsys scoring error %s: %s' % (user_id, e, source_candidate_map), exc_info=True)
    return source_candidate_map

def post_pool_creation(user_id:int, source_candidate_map:dict[str, list[PostInfo]], source_list:list[str]):
    post_id_pool = set()
    for source in source_list:
        if source in source_candidate_map:
            post_id_pool |= set([post_info.pid for post_info in source_candidate_map[source]])
    work_logger.info('User: %s. Scoring id pool set: %s' % (user_id, post_id_pool))
    return post_id_pool

def update_source_candidate_map(source_candidate_map:dict[str, list[PostInfo]], post_scores_map:dict[int, float], source_list:list[str]):
    for source in source_list:
        if source in source_candidate_map:
            for post_info in source_candidate_map[source]:
                if post_info.pid in post_scores_map:
                    post_info.post_score_info['score'] *= post_scores_map[post_info.pid]
    return source_candidate_map

@log_func_time
def random_post_selection(source_candidate_map:dict[str, list[PostInfo]], number:int) -> dict[str, list[PostInfo]]:
    for source in source_candidate_map:
        source_candidate_map[source] = result_prob_random_change(source_candidate_map[source], number)
    return source_candidate_map