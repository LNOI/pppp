from src.utils.db_utils import execute_raw_query
from src.common.post_info_class import PostInfo
from src.const import const_map as CONST_MAP

def feature_post_source(filters):
    query = '''
    select p.id
    from eligible_posts p
    where p.user_id in (
        select id
        from account_user au
        where au.account_level_id in (
            select id
            from account_level al
            where al.slug like 'curator%%'
        )
    )
    -- and p.is_public = true -- not unpublic
    -- and p.is_deleted = false -- not deleted
    '''
    for filter_func in filters:
        query = filter_func(query)
    res = execute_raw_query(query)
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result

def featured_post_business_acc_source(filters) -> list[PostInfo]:
    query = '''
    select p.id
    from top_posts p     
    where p.user_id = ANY (         
        select id         
        from top_sellers ts  
    )     
    -- and p.is_public = true -- not unpublic
    -- and p.is_deleted = false -- not deleted
    '''
    for filter_func in filters:
        query = filter_func(query)
    res = execute_raw_query(query)
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result


def following_post_source(user_id, filters):
    query = f'''
    select p.id
    from top_posts p
    where p.is_deleted = false
    and p.is_sold = false
    and p.user_id in (
        select user_id
        from account_following af
        where af.followed_by = {user_id}
    )
    --and p.is_public = true -- not unpublic
    --and p.is_deleted = false -- not deleted
    '''
    for filter_func in filters:
        query = filter_func(query)
    res = execute_raw_query(query)
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result