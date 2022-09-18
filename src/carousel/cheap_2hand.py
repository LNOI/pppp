from src.common.post_info_class import add_post_score_info, PostInfo
from src.const import const_map as CONST_MAP
from src.common.random_shuffle import random_post_info_shuffle

from functools import partial
from src.common.source.post_pool import eligible_post_source
from src.common.filter.post_sql_filter import gender, pricing_less
from src.common.filter.order_limit import add_order, add_row_limit

def get_cheap_2hand_info(male_item=False) -> list[PostInfo]:
    filters = []
    if male_item is True:
        filters.append(partial(gender, gender_ids=[1]))
    filters.append(partial(pricing_less, amount=50000))
    filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_processed_cheap_2hand_post_info() -> list[PostInfo]:
    post_infos = get_cheap_2hand_info()
    add_post_score_info(post_infos)
    post_infos = random_post_info_shuffle(post_infos)
    return post_infos

def get_cheap_2hand_post() -> dict[str,list[int]]:
    post_ids = [pi.pid for pi in get_processed_cheap_2hand_post_info()][:CONST_MAP.post_limit_medium]
    return {'post_ids':post_ids}