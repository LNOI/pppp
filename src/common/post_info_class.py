from typing import Union
import numpy as np
from src.utils.db_utils import execute_raw_query
from src.utils.try_convert import try_int, try_float
from src.common.score_decay import post_score_modify

import logging
logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
class PostInfo():
    def __init__(self, pid:int=-1, value_map:dict=None):
        if value_map is not None and 'pid' in value_map and 'post_score_info' in value_map and 'source_specific_info' in value_map:
            self.pid = int(value_map['pid'])
            self.post_score_info = value_map['post_score_info']
            self.source_specific_info = value_map['source_specific_info']
        else:
            self.pid = pid
            self.post_score_info = {}
            self.source_specific_info = {}
    def to_json(self):
        return {
            'pid':self.pid,
            'post_score_info':self.post_score_info,
            'source_specific_info':self.source_specific_info
        }
    def __repr__(self):
        return str(self.pid)
    def __str__(self):
        return str(self.pid)


def add_post_score_info_to_source_map(post_info_list_map:dict[str,list[PostInfo]]) -> None:
    post_id_pool = []
    for key in post_info_list_map:
        for post_info in post_info_list_map[key]:
            post_id_pool.append(post_info.pid)
    info_pool_map = cal_post_score_info(post_id_pool)
    for key in post_info_list_map:
        for post_info in post_info_list_map[key]:
            if post_info.pid in info_pool_map:
                post_info.post_score_info = info_pool_map[post_info.pid].copy()
        for i in range(len(post_info_list_map[key]) - 1, 0, -1):
            if 'score' not in post_info_list_map[key][i].post_score_info:
                del post_info_list_map[key][i]
        # add_commitment_score(post_info_list_map[key])

def add_post_score_info(post_info_list:list[PostInfo]) -> None:
    post_id_pool = [pi.pid for pi in post_info_list]
    info_pool_map = cal_post_score_info(post_id_pool)
    for post_info in post_info_list:
        if post_info.pid in info_pool_map:
            post_info.post_score_info = info_pool_map[post_info.pid].copy()
    for i in range(len(post_info_list) - 1, 0, -1):
        if 'score' not in post_info_list[i].post_score_info:
            del post_info_list[i]
    # add_commitment_score(post_info_list)

def cal_post_score_info(post_id_pool:list[int]) -> dict[int, dict]:
    if len(post_id_pool) < 1:
        return {}
    query = '''select p.id, 
    p.ai_metadata -> 'post_score' -> 'total' as score, 
    date_part('day', now() - p.created_at) as post_age, 
    date_part('day', now() - au.last_online) as last_online, 
    (p.ai_metadata->'user_ordinal')::int as user_ordinal
    from eligible_posts p join account_user au on p.user_id = au.id
    where p.id in :post_ids
    '''
    res = execute_raw_query(query, post_ids = tuple(set(post_id_pool)))
    result = {}
    for pid, db_raw_score, db_post_age, db_last_online, db_user_ordinal in res:
        if pid is None:
            continue
        raw_score = try_float(db_raw_score, 0)
        post_age = try_int(db_post_age, 60)
        last_online = try_int(db_last_online, 60)
        user_ordinal = try_int(db_user_ordinal, -1)
        result[pid] = {
            'raw_score':raw_score,
            'post_age':post_age,
            'last_online':last_online,
            'user_ordinal':user_ordinal,
            'score_component':'post_score'
        }
        result[pid]['score'] = post_score_modify(raw_score, post_age, last_online, user_ordinal)
    return result

from src.common.commitment_score import get_commitment_score
def add_commitment_score(post_info_list:list[PostInfo]):
    special_score_map = get_commitment_score()
    for post_info in post_info_list:
        if post_info.pid in special_score_map and special_score_map[post_info.pid] != 0:
                post_info.post_score_info['commitment_score'] = special_score_map[post_info.pid]
        else:
            post_info.post_score_info['commitment_score'] = 1
        post_info.post_score_info['score'] /= post_info.post_score_info['commitment_score']


from src.recommendation.utils.recsys_scoring import post_vec_query, get_new_post_scores
def add_post_recsys_score(post_infos:list[PostInfo], user_vector:Union[list[float], np.ndarray]):
    user_vector = np.array(user_vector).reshape(-1)
    post_ids = [pi.pid for pi in post_infos]
    post_tup = post_vec_query(post_ids)
    post_recsys_score = get_new_post_scores(post_tup, user_vector)
    for pi in post_infos:
        if pi.pid in post_recsys_score:
            pi.post_score_info['personalized_coef'] = post_recsys_score[pi.pid]
        else:
            pi.post_score_info['personalized_coef'] = 1
        if 'score' not in pi.post_score_info:
            deviation_logger.info('Post %s do not have score before adding user recsys score' % pi.pid, exc_info=True)
            pi.post_score_info['score'] = 1.0
        pi.post_score_info['score'] *= pi.post_score_info['personalized_coef']
        if pi.post_score_info['score'] <= 0:
            pi.post_score_info['score'] = 1e-4
        if 'score_component' not in pi.post_score_info:
            deviation_logger.info('Post %s do not have score_component before adding user recsys score' % pi.pid, exc_info=True)
            pi.post_score_info['score_component'] = ''
        pi.post_score_info['score_component'] += '|personalized_coef'
