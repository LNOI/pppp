from src.common.current_time import get_query_time_str
from src.utils.redis_caching import redis_cache_list
from src.utils.db_utils import execute_raw_query
from src.utils.decorator import log_func_time
from typing import Tuple, List, Dict

@log_func_time
def get_following_post_info(user_id:int, hour_limit:int) -> List[int]:
    post_ids = query_following_post(user_id, hour_limit)
    post_ids = [int(i) for i in post_ids]
    return post_ids

@log_func_time
@redis_cache_list(lambda x, y: 'following:%s:%s:ids' % (str(x), str(y)), expire_secs=3600)
def query_following_post(user_id:int, hour_limit:int) -> List[int]:
    query = '''
    select p.id
    -- from account_following a join post p on a.user_id = p.user_id
    -- where followed_by = :user_id
    from post p
    where  p.is_deleted = false
    and p.is_sold = false
    and p.created_at >= %s - interval ':hour_limit hours'
    and p.user_id in (
        select user_id
        from account_following af
        where af.followed_by = :user_id
    )
    ''' % get_query_time_str()
    query_result = execute_raw_query(query, user_id=user_id, hour_limit=hour_limit)
    if len(query_result) > 0:
        post_ids = [int(i[0]) for i in query_result]
    else:
        post_ids = []
    return post_ids
