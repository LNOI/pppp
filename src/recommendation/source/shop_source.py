import random
from src.common.post_info_class import PostInfo
from src.utils.query.user_post import get_user_post_info
from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.utils.decorator import log_func_time
from typing import Dict, List

@log_func_time
def shop_post_raw() -> list[PostInfo]:
    shop_query = '''select id
from top_sellers au 
where au.account_level_id in (
    select id
    from account_level al 
    where al.slug like 'subscription%%'
)
'''
    res = execute_raw_query(shop_query)
    shop_ids = [int(item[0]) for item in res]
    shop_results = get_user_post_info(shop_ids, CONST_MAP.shop_post_day_limit)
    return [PostInfo(post_id) for post_id in shop_results]

def shop_queue_for_hashtag() -> Dict[int, List[int]]:
    query = '''
    select p.id, p.user_id from post p
    where p.user_id in (
        select id
        from account_user au
        where au.account_level_id in (
            select id
            from account_level al
            where al.slug like 'subscription%%'
        )
        order by random()
        limit 1
    )
    order by p.total_favorites::float/ (case when is_sold then 3 else 1 end)
    limit :limit
    '''
    res = execute_raw_query(query, limit=CONST_MAP.post_limit_small)
    return post_shop_map_from_query_result(res)


def post_shop_map_from_query_result(tup_list):
    post_shop_map = {}
    for pid, sid in tup_list:
        shop_id = int(sid)
        if shop_id not in post_shop_map:
            post_shop_map[shop_id] = []
        post_id = int(pid)
        post_shop_map[shop_id].append(post_id)
    return post_shop_map
