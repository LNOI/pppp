from src.common.post_info_class import add_post_score_info, PostInfo
from src.common.random_shuffle import random_post_info_shuffle
from src.const import const_map as CONST_MAP

from functools import partial
from src.common.source.post_pool import eligible_post_source
from src.common.filter.post_sql_filter import gender
from src.common.filter.order_limit import add_order, add_row_limit
from src.utils.redis_caching import redis_cache_json

def get_male_post_info() -> list[PostInfo]:
    gender_func = partial(gender, gender_ids=[1])
    order_func = partial(add_order, order_cols=['score'], direction=['desc'])
    limit_func = partial(add_row_limit, limit=CONST_MAP.post_limit_big)
    post_infos = eligible_post_source([gender_func, order_func, limit_func])
    return post_infos

@redis_cache_json(key_maker=lambda: 'source:male_item', expire_secs=3600)
def get_processed_male_item_infos():
    post_infos = get_male_post_info()
    add_post_score_info(post_infos)
    post_infos = random_post_info_shuffle(post_infos)
    return [pi.to_json() for pi in post_infos]

def get_male_items(number_of_item):
    post_infos = [PostInfo(value_map=pi_json) for pi_json in get_processed_male_item_infos()]
    post_ids = [pi.pid for pi in post_infos][:CONST_MAP.post_limit_medium]
    return {'post_ids':post_ids}