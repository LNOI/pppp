from src.common.post_info_class import PostInfo
from src.const import const_map as CONST_MAP

from functools import partial
from src.common.source.post_pool import eligible_post_source, hashtag_post_source
from src.common.filter.post_sql_filter import in_candidate, avoid_keyword, new_arrival, is_for_sale
from src.common.filter.order_limit import add_order, add_row_limit

# def get_user_post_info(user_ids:list[int], male_item=False) -> list[PostInfo]:
#     filters = []
#     if male_item is True:
#         filters.append(partial(gender, gender_ids=[1,3]))
#     filters.append(partial(belong_to_user, user_ids))
#     filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
#     filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
#     post_infos = eligible_post_source(filters)
#     return post_infos

def get_caption_filtered_post_info(post_ids:list[int], keywords:list[str], male_item=False) -> list[PostInfo]:
    filters = []
    filters.append(partial(in_candidate, candidates=post_ids))
    filters.append(partial(avoid_keyword, keywords=keywords))
    filters.append(partial(add_order, order_cols=['score'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_like_ordered_post_info() -> list[PostInfo]:
    filters = []
    filters.append(partial(new_arrival, days=30))
    filters.append(partial(add_order, order_cols=['total_favorites'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_hashtag_like_ordered_post_info(hashtag_ids:list[int], for_sale=True) -> list[PostInfo]:
    filters = []
    filters.append(partial(is_for_sale, for_sale=for_sale))
    filters.append(partial(add_order, order_cols=['total_favorites'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = hashtag_post_source(filters, hashtag_ids)
    return post_infos