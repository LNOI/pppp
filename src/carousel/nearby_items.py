import random

from functools import partial
from src.common.post_info_class import PostInfo, add_post_score_info
from src.common.random_shuffle import random_post_info_shuffle
from src.common.more_utils import get_user_address
from src.common.source.post_pool import eligible_post_source
from src.common.filter.post_sql_filter import gender, is_nearby, pricing_inrange, pricing_more
from src.common.filter.order_limit import add_order, add_row_limit
from src.common.random_shuffle import random_shuffle
from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.common.post_info_class import PostInfo


def get_flashsale_post_info(male_item=False, shop_ids=[], price_list=[]) -> list[PostInfo]:
    if male_item:
        gender_id = [1,3]
    else:
        gender_id = [2,3]

    query = '''
    select p.id
    from top_posts p 
    where user_id in :shop_ids
    and p.amount in :price_list
    -- and p.original_price is not null
    and p.gender_id in :gender_id
    -- and p.is_sold = false
    -- and p.is_deleted = false
    -- order by (p.ai_metadata->'post_score'->'total')::float desc
    -- order by p.amount asc, (p.ai_metadata->'post_score'->'total')::float desc
    order by p.amount asc, array_position(ARRAY[%s]::int[], p.user_id), (p.ai_metadata->'post_score'->'total')::float desc
    ''' % ','.join(['%s' % id for id in shop_ids])

    res = execute_raw_query(query, shop_ids=tuple(shop_ids), price_list=tuple(price_list), gender_id=tuple(gender_id))
    post_infos = []
    for pid, in res:
        if pid is None:
            continue
        pi = PostInfo(int(pid))
        post_infos.append(pi)

    return post_infos


def get_flashsale_shop_info(number_of_hashtag: int, male_item=False, shop_ids=[], price_list=[]):
    if male_item:
        gender_id = [1,3]
    else:
        gender_id = [2,3]

    query = '''
    select p.id, p.user_id
    from top_posts p 
    where user_id in :shop_ids
    -- and p.amount in :price_list
    -- and p.original_price is not null
    -- and p.gender_id in :gender_id
    -- and p.is_sold = false
    -- and p.is_deleted = false
    -- order by (p.ai_metadata->'post_score'->'total')::float desc
    -- order by p.amount asc, (p.ai_metadata->'post_score'->'total')::float desc
    order by array_position(ARRAY[%s]::int[], p.user_id), p.amount asc, (p.ai_metadata->'post_score'->'total')::float desc
    ''' % ','.join(['%s' % id for id in shop_ids])

    res = execute_raw_query(query, shop_ids=tuple(shop_ids), price_list=tuple(price_list), gender_id=tuple(gender_id))

    post_shop_map = {}
    for pid, sid in res:
        shop_id = int(sid)
        if shop_id not in post_shop_map:
            post_shop_map[shop_id] = []
        post_id = int(pid)
        post_shop_map[shop_id].append(post_id)
    shop_ids = list(post_shop_map.keys())
    
    if len(shop_ids) > 0:
        # random.shuffle(shop_ids)
        sss_id_query = '''
        select au.sss_id 
        from top_sellers au
        where au.id in :shop_id
        order by array_position(ARRAY[%s]::int[], au.id)
        ''' % ','.join(['%s' % id for id in shop_ids])

        res = execute_raw_query(sss_id_query, shop_id=tuple(shop_ids))
        shop_hashtag = []
        for shop_data, shop_id in zip(res, shop_ids):
            sss_id = str(shop_data[0])
            shop_hashtag.append(
                {
                    'hashtag': '#%s' % sss_id, 
                    'total_post': len(post_shop_map[shop_id]), 
                    'post_id':post_shop_map[shop_id], 
                    'subtitle':'Được tài trợ'
                }
            )
    else:
        return []

    final = shop_hashtag
    for item in final:
        if 'post_scores' in item:
            # item['post_id'] = random_shuffle(item['post_id'], item['post_scores'])
            del item['post_scores']
    return final[:number_of_hashtag]


def get_merchandise_post_info(user_id, male_item=False, address_level = 0, min_price = 150000) -> list[PostInfo]:
    filters = []
    if male_item is True:
        filters.append(partial(gender, gender_ids=[1]))
    if address_level > 0:
        user_address = get_user_address(user_id, address_level)
        filters.append(partial(is_nearby, user_address = user_address))
    if min_price > 0:
        filters.append(partial(pricing_more, amount = min_price))

    filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos


def get_nearby_post_info(user_id, male_item=False) -> list[PostInfo]:
    filters = []
    if male_item is True:
        filters.append(partial(gender, gender_ids=[1]))
    user_address = get_user_address(user_id)
    filters.append(partial(is_nearby, user_address = user_address))
    filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos


def get_processed_nearby_item_infos(user_id):
    post_infos = get_nearby_post_info(user_id)
    add_post_score_info(post_infos)
    post_infos = random_post_info_shuffle(post_infos)
    return post_infos


def get_nearby_items(user_id):
    post_ids = [pi.pid for pi in get_processed_nearby_item_infos(user_id)][:CONST_MAP.post_limit_medium]
    return {'post_ids':post_ids}
