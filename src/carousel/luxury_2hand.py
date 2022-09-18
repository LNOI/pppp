from numpy import add
from src.common.post_info_class import add_post_score_info, PostInfo
from src.const import const_map as CONST_MAP
from src.common.random_shuffle import random_post_info_shuffle

from functools import partial
from src.common.source.post_pool import eligible_post_source
from src.common.filter.post_sql_filter import gender, pricing_more, have_brand
from src.common.filter.order_limit import add_order, add_row_limit

def get_luxury_2hand_post_info(male_item=False) -> list[PostInfo]:
    filters = []
    if male_item is True:
        filters.append(partial(gender, gender_ids=[1]))
    filters.append(partial(pricing_more, amount=500000))
    filters.append(have_brand)
    filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_processed_luxury_2hand_post_infos():
    post_infos = get_luxury_2hand_post_info()
    add_post_score_info(post_infos)
    post_infos = random_post_info_shuffle(post_infos)
    return post_infos

def get_luxury_2hand_post():
    post_ids = [pi.pid for pi in get_processed_luxury_2hand_post_infos()][:CONST_MAP.post_limit_medium]
    return {'post_ids':post_ids}