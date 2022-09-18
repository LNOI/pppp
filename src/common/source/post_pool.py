from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.common.post_info_class import PostInfo

# we need to cache this
def get_curator_items(filters) -> list[PostInfo]:
    query = '''
    select id
    from post p 
    where p.user_id = 1083256
    order by random()
    limit 100
    '''
    res = execute_raw_query(query)
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result

def top_post_source(filters) -> list[PostInfo]:
    query = '''
    select id
    from top_posts p 
    where 1=1
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

def eligible_post_source(filters) -> list[PostInfo]:
    query = '''
    select p.id
    from eligible_posts p
    where 1=1
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

def get_remind_items(user_id):
    query = '''
    with sample as (
        select ccl.post_id, 1.5 as rank -- priority items from cart
        from checkout_checkout cc 
        left join checkout_checkoutline ccl on cc."token"  = ccl.checkout_id 
        where 1=1 
        and cc.user_id = :user_id 
        union
        select p.id as post_id, 1 as rank
        from post p 
        where 1=1
        and p.user_id in (
            select af.user_id -- from following
            from account_following af 
            where af.followed_by = :user_id
            union
            select oo.seller_id -- from bought shop
            from order_order oo 
            where oo.user_id = :user_id 
            and status != 'cancelled'
        )
    	and p.created_at > current_date - interval '2 weeks'
    )
    select s.post_id
    from sample s 
    join eligible_posts p on p.id = s.post_id -- egi post
    where 1=1
    and p.user_id in (
        select id -- top_sellers filter
        from top_sellers ts 
    )
    order by random() * p.score * s.rank
    limit :limit
    '''

    res = execute_raw_query(query, user_id = user_id, limit=CONST_MAP.post_limit_small)
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result

def full_post_source(filters) -> list[PostInfo]:
    query = '''
    select p.id
    from eligible_posts p
    where p.is_public = true -- not unpublic
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

def hashtag_post_source(filters, hashtag_ids:list[int]) -> list[PostInfo]:
    query = '''
    select p.id
    from post p join hashtag_post hp on p.id = hp.post_id
    where p.is_public = true -- not unpublic
    and p.is_deleted = false -- not deleted
    and hp.hashtag_id in :hashtag_ids
    '''
    for filter_func in filters:
        query = filter_func(query)
    res = execute_raw_query(query, hashtag_ids=tuple(hashtag_ids))
    result = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        result.append(pi)
    return result