import random

from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.utils.redis_caching import redis_cache_json


def get_june_week_2_post_ids(shop_ids:list[int]):
    query = '''
    with sample as(
    select user_id,id,row_number()over(partition by user_id order by id ASC ) as rownum 
    from post
    where user_id in :shop_ids
    )
    select user_id, array_agg(id) as post_ids
    from sample
    where rownum<=20
    group by 1
    '''
    shop_res = execute_raw_query(query, shop_ids=tuple(shop_ids))
    return [list(i) for i in shop_res]

def get_represent_shop_id_from_post_ids(post_ids:list[int]) -> list[int]:
    if len(post_ids) < 1:
        return []
    shop_limit = 5
    query = '''
    with top_shops as (
        select user_id, random() * (1 + sum(p.total_favorites))::float/sqrt(count(*)) as score
        from eligible_posts p
        where p.id in :post_ids
        -- and p.is_deleted = false
        -- and p.is_for_sale = true
        group by 1
    )
    select user_id 
    from top_shops ts left join eligible_users au on ts.user_id = au.id
    where au.is_business_acc = true
    order by ts.score * (au.total_followers + 1)
    limit :limit
    '''
    shop_res = execute_raw_query(query, post_ids=tuple(post_ids), limit = shop_limit)
    return [int(i[0]) for i in shop_res]


@redis_cache_json(lambda x: 'shop_content:%s' % x, expire_secs=3600)
def get_raw_content_post_ids(user_id:int) -> list[int]:
    # content_query = '''(
    #     select p.id
    #     from post p 
    #     where p.user_id = :user_id
    #     and p.is_deleted = false 
    #     and p.is_public = true
    #     and p.is_sold = false
    #     order by p.total_favorites desc
    #     limit 6
    # )
    # union
    # (
    #     select p.id
    #     from post p 
    #     where p.user_id = :user_id
    #     and p.is_deleted = false 
    #     and p.is_public = true
    #     and p.is_sold = false
    #     and p.id not in (
    #     select p.id
    #     from post p 
    #     where p.user_id = :user_id
    #     and p.is_deleted = false 
    #     and p.is_public = true
    #     and p.is_sold = false
    #     order by p.total_favorites desc
    #     limit 6
    # )
    # order by p.created_at desc
    # limit :limit
    # )
    # '''
    content_query = '''
        select p.id
        from eligible_posts p 
        where p.user_id = :user_id
        order by p.total_favorites desc
        limit 12
    '''
    post_res = execute_raw_query(content_query, user_id=user_id, limit=CONST_MAP.post_limit_medium)
    content_post_ids = [int(i[0]) for i in post_res][:CONST_MAP.post_limit_medium]
    return content_post_ids


def get_content_post_ids(user_id:int) -> list[int]:
    content_post_ids = get_raw_content_post_ids(user_id)
    random.shuffle(content_post_ids)
    return content_post_ids


@redis_cache_json(lambda x: 'shop_thumbnail:%s' % x, expire_secs=3600)
def get_user_thubmnail_post_id(user_id:int) -> list[int]:
    thumbnail_post_query = '''
        select p.id
        from eligible_posts p 
        where p.user_id = :user_id
        order by p.total_favorites desc
        limit 6
    '''

    post_res = execute_raw_query(thumbnail_post_query, user_id=user_id)
    thumbnail_post_ids = [int(i[0]) for i in post_res]
    return thumbnail_post_ids
