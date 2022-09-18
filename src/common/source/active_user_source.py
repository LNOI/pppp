from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query


def promoted_sellers_source():
    query = '''
    select id, sss_id, account_level_id, (au.ai_metadata->'user_score')::float
    from account_user au 
    where 1=1
    and au.id in (select id from eligible_users eu)
    and account_level_id not in (3, 6, 98, 99)
    and total_posts > 0
    and id not in (866216, 866268) -- SBasique, Spromo
    and subscription_until > now() - interval '1 month'
    order by au.account_level_id desc, random() * (au.ai_metadata->'user_score')::float desc
    limit :limit
    '''
    res = execute_raw_query(query, limit=CONST_MAP.post_limit_small)
    return [int(i[0]) for i in res]


def top_sellers_source(filters):
    query = '''
    select es.id 
    from top_sellers es 
    where true
    -- and es.total_posts >= 10
    '''
    for filter_func in filters:
        query = filter_func(query)
    res = execute_raw_query(query)
    return [int(i[0]) for i in res]


def eligible_users_filter(uids: list):
    query = '''
    select id
    from eligible_users es 
    where 1=1 
    and es.id in :uids
    -- and es.is_blocked=false
    '''
    res = execute_raw_query(query, uids=tuple(uids))
    return [int(i[0]) for i in res]