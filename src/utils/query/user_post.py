from src.common.current_time import get_query_time_str
from src.utils.redis_caching import redis_cache_list
from src.utils.db_utils import execute_raw_query

def get_user_post_info(user_ids:list[int], day_limit:float, post_limit:float=1000, keep_sold:bool=True) -> list[int]:
    if len(user_ids) < 1:
        return []
    post_ids = query_user_post(user_ids, day_limit, post_limit, keep_sold)
    post_ids = [int(i) for i in post_ids]
    return post_ids

def user_key_maker(user_ids:list[int], day_limit:float, post_limit:float=1000, keep_sold:bool=True) -> str:
    return 'user:%s:%s' % ('-'.join([str(i) for i in user_ids]), str(day_limit))

@redis_cache_list(user_key_maker, expire_secs=3600)
def query_user_post(user_ids:list[int], day_limit:float, post_limit:float=1000, keep_sold:bool=True) -> list[int]:
    if keep_sold:
        query = '''
        select p.id from post p
        where p.user_id in :user_ids 
        and p.created_at >= %s - interval ':day_limit days' 
        and p.is_deleted = false
        order by created_at desc limit :post_limit
        ''' % get_query_time_str()
    else:
        query = '''
        select p.id from post p
        where p.user_id in :user_ids 
        and p.created_at >= %s - interval ':day_limit days' 
        and p.is_deleted = false 
        and p.is_sold = false
        order by created_at desc limit :post_limit
        ''' % get_query_time_str()
    query_result = execute_raw_query(query, user_ids=tuple(user_ids), day_limit=day_limit, post_limit=post_limit)
    if len(query_result) > 0:
        return [int(i[0]) for i in query_result]
    return []
