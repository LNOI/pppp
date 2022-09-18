from src.utils.db_utils import execute_raw_query
from src.utils.decorator import log_func_time
import logging
work_logger = logging.getLogger('work_logger')
import random

@log_func_time
def get_boost_coefs(post_ids: list[int]) -> list[float]:
    if len(post_ids) <= 0:
        return []
    query = '''
    select p.id, p.ai_metadata->'post_score'->'total' as score 
    from eligible_posts p 
    where p.id in :post_ids
    '''
    res = execute_raw_query(query, post_ids=tuple(post_ids))
    score_map = {int(pid):float(score) if score is not None else 0 for pid, score in res}
    scores = [random.uniform(0, 1e-4) + float(score_map[pid]) if pid in score_map else random.uniform(0, 1e-4) for pid in post_ids]
    return scores
