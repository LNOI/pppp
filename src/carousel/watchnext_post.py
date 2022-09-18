from functools import partial

from src.common.filter.order_limit import add_order, add_row_limit, add_order_top_posts
from src.common.filter.post_sql_filter import *
from src.common.post_info_class import PostInfo

from src.common.source.watchnext_source import feature_post_source, featured_post_business_acc_source, following_post_source
from src.common.source.popular_source import popular_post_source
from src.common.source.post_pool import eligible_post_source, full_post_source, top_post_source, get_remind_items, get_curator_items

from src.const import const_map as CONST_MAP
from src.recommendation.source.recsys_source import recsys_post_raw
from src.utils.db_utils import execute_raw_query
from src.advertising.ads_util import check_ads_type
from src.utils.decorator import anonymous_user

def fill_default_value(filter_args):
    if type(filter_args) is not dict:
        filter_args = {}
    if 'user_id' not in filter_args:
        filter_args['user_id'] = -1
    for field in ['category', 'size', 'condition', 'sex', 'price']:
        if field not in filter_args:
            filter_args[field] = []
    return filter_args

def get_curator_source(filter_args, limit=-1) -> list[PostInfo]:
    if 'user_id' not in filter_args:
        filter_args['user_id'] = -1    
    
    post_infos = get_curator_items(filter_args)
    return post_infos    

def get_remind_source(filter_args, limit=-1) -> list[PostInfo]:
    if 'user_id' not in filter_args:
        filter_args['user_id'] = -1    
    
    if filter_args['user_id'] == -1: #anonymous user or unknown user
        return []
    post_infos = get_remind_items(filter_args['user_id'])
    return post_infos    

def get_brand_mall_post_info(filter_args, limit=-1) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    # filter args from client
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))

    # mall condition
    # filters.append(partial(account_level, account_level_ids='21,22,23,24,25'))
    filters.append(partial(is_business_acc))
    filters.append(partial(avoid_sold_post))

    # order by post scroing, priority VFit   
    # filters.append(partial(add_order, order_cols=["random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc']))
    filters.append(partial(add_order, order_cols=["user_id in (select id from account_user where account_level_id = 25)", "random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc', 'desc']))
    # size of result
    if limit < 1:
        limit = CONST_MAP.post_limit_small
    filters.append(partial(add_row_limit, limit=limit))    
    
    # query and adding filters
    # post_infos = top_post_source(filters)
    post_infos = eligible_post_source(filters)
    return post_infos


def get_mall_post_info(filter_args, limit=-1) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    # filter args from client
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))

    # mall condition
    # filters.append(partial(account_level, account_level_ids='21,22,23,24,25'))
    filters.append(partial(is_business_acc))
    filters.append(partial(avoid_sold_post))

    # order by post scroing, priority VFit   
    # filters.append(partial(add_order, order_cols=["random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc']))
    filters.append(partial(add_order, order_cols=["user_id in (select id from top_sellers)", "random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc', 'desc']))
    # size of result
    if limit < 1:
        limit = CONST_MAP.post_limit_small
    filters.append(partial(add_row_limit, limit=limit))    
    
    # query and adding filters
    # post_infos = top_post_source(filters)
    post_infos = eligible_post_source(filters)
    return post_infos

def get_2hand_post_info(filter_args, limit=-1) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    # filter args
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))

    # 2hand source
    filters.append(partial(total_view_greater,limit=CONST_MAP.secondhand_limit_view) )
    filters.append(partial(secondhand)) 
    # filters.append(partial(from_top_seller)) -- order by (soft filtering) instead of hard condition

    # ordering
    filters.append(partial(add_order, order_cols=["user_id in (select id from top_sellers)", "random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc', 'desc']))

    # size of result
    if limit < 1:
        limit = CONST_MAP.post_limit_small
    filters.append(partial(add_row_limit, limit=limit))    
    
    # query and adding filters
    post_infos = eligible_post_source(filters)
    return post_infos


def get_new_post_info(filter_args, limit=-1) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    # filter args
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))

    # new source
    filters.append(partial(newitem)) #filter_args['time_limit']))
    filters.append(partial(from_top_seller))

    # ordering
    filters.append(partial(add_order, order_cols=["user_id in (select id from top_sellers)", "random() * score + case when (ai_metadata->'virtual_fit'->>'data') != '[]' then 0 else 0.5 end"], direction=['desc', 'desc']))

    # size of result
    if limit < 1:
        limit = CONST_MAP.post_limit_small
    filters.append(partial(add_row_limit, limit=limit))    
    
    # query and adding filters
    post_infos = eligible_post_source(filters)
    return post_infos

def get_simple_filtered_post_info(post_ids, filter_args, limit=-1) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    filters.append(partial(in_candidate, candidates=post_ids))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    filters.append(partial(add_order, order_cols=['created_at'], direction=['desc']))
    if limit < 1:
        limit = CONST_MAP.post_limit_small
    filters.append(partial(add_row_limit, limit=limit))
    # post_infos = full_post_source(filters)
    post_infos = eligible_post_source(filters)
    return post_infos

def get_curating_featured_post_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=['created_at'], direction=['desc']))
    filters.append(partial(add_order_top_posts, order_cols=['created_at'], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_small))
    post_infos = feature_post_source(filters)
    return post_infos

def get_business_feature_post_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    filters.append(partial(new_arrival, days=CONST_MAP.time_limit_long))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=["(p.ai_metadata->'post_score'->'total')::float"], direction=['desc']))
    filters.append(partial(add_order_top_posts, order_cols=["(p.ai_metadata->'post_score'->'total')::float"], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_small))
    post_infos = featured_post_business_acc_source(filters)
    return post_infos

def get_featured_post_info(filter_args) -> list[PostInfo]:
    curating_source = get_curating_featured_post_info(filter_args)
    business_source = get_business_feature_post_info(filter_args)
    appeared_pid = []
    deduplicated_result = []
    for pi in curating_source + business_source:
        if pi.pid not in appeared_pid:
            deduplicated_result.append(pi)
            appeared_pid.append(pi.pid)
    return deduplicated_result


def get_following_post_info(user_id, filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filter_args['user_id'] = user_id
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    filters.append(partial(new_arrival, days=1))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=["(p.ai_metadata -> 'post_score' -> 'total')::float"], direction=['desc']))
    filters.append(partial(add_order_top_posts, order_cols=["(p.ai_metadata -> 'post_score' -> 'total')::float"], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_small))
    post_infos = following_post_source(user_id, filters)
    return post_infos

def get_newpost_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    # filters.append(partial(total_view_greater, limit=CONST_MAP.newpost_view_limit))
    filters.append(partial(new_arrival, days=filter_args['time_limit']))
    filters.append(metadata_exist)
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=["p.total_views","(p.ai_metadata -> 'post_score' -> 'total')::float"], direction=['<=%s' % (CONST_MAP.newpost_view_limit),'desc']))
    filters.append(partial(add_order_top_posts, order_cols=["p.total_views","(p.ai_metadata -> 'post_score' -> 'total')::float"], direction=['<=%s' % (CONST_MAP.newpost_view_limit),'desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_small))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_newpost_2hand_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    # filters.append(partial(total_view_greater, limit=CONST_MAP.newpost_view_limit))
    filters.append(partial(new_arrival, days=filter_args['time_limit']))
    filters.append(metadata_exist)
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=["(p.ai_metadata -> 'post_score' -> 'total')::float"], direction=['desc']))
    filters.append(partial(add_order_top_posts, order_cols=["(p.ai_metadata -> 'post_score' -> 'total')::float * random()"], direction=['desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_small))
    filters.append(partial(new_arrival, days=7)) #filter_args['time_limit']))
    filters.append(partial(secondhand)) #filter_args['time_limit']))

    post_infos = eligible_post_source(filters)
    new_post_ids = [pi.pid for pi in post_infos]
    # filtered_post_ids = filter_2hand(new_post_ids)
    return [pi for pi in post_infos if pi.pid in new_post_ids]

    
def get_popular_post_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    if 'avoid_categories' in filter_args:
        filters.append(partial(avoid_category, categories=filter_args['avoid_categories']))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=['row', 'score'], direction=['asc', 'desc']))
    filters.append(partial(add_order_top_posts, order_cols=['row', 'score'], direction=['asc', 'desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = popular_post_source(filters)
    return post_infos

def get_popular_business_post_info(filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    filters.append(is_business_acc)
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # filters.append(partial(add_order, order_cols=['row', 'score'], direction=['asc', 'desc']))
    filters.append(partial(add_order_top_posts, order_cols=['row', 'score'], direction=['asc', 'desc']))
    filters.append(partial(add_row_limit, limit=CONST_MAP.post_limit_big))
    post_infos = popular_post_source(filters)
    return post_infos

def get_recsys_post_info(user_id, filter_args) -> list[PostInfo]:
    filter_args = fill_default_value(filter_args)
    filter_args['user_id'] = user_id
    candidate_ids = [pi.pid for pi in recsys_post_raw(user_id)]
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    filters.append(partial(in_candidate, candidates=candidate_ids))
    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    if 'keep_sold_post' not in filter_args:
        filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    filters.append(partial(add_order_top_posts))
    post_infos = eligible_post_source(filters)
    return post_infos

def get_shop_post_info(filter_args, request_type, user_id=None) -> list[PostInfo]:

    # if CONST_MAP.test_mode == True and user_id in CONST_MAP.home_api_test_user:
    ads_type = 'discovery_trending' if request_type == 'trending' else 'discovery_4you'
    ads_object = check_ads_type(ads_type=ads_type)
    shop_query = '''
        with rank_table as (
            select row_number() over (partition by pop.user_id order by random() * (pop.ai_metadata->'post_score'->'total')::numeric desc) as r, pop.*
            from top_posts pop 
            Where 1=1
            and pop.account_level_id in :ads_object --(3)
            --and pop.account_level_id in (22,23,24)
            --and pop.account_level_id in (23,24)
            --and id in (%s)
        )
        select id
        from rank_table
        where r = 1
        order by random() * (account_level_id - 20)
    '''

    res = execute_raw_query(shop_query, ads_object=tuple(ads_object))
    shop_ids = [int(item[0]) for item in res]

    filter_args = fill_default_value(filter_args)
    filters = []
    if 'have_keyword' in filter_args:
        filters.append(partial(have_any_keyword, keywords=filter_args['have_keyword']))
    # filters.append(partial(belong_to_user, user_ids=shop_ids))
    filters.append(partial(new_arrival, days=CONST_MAP.shop_post_day_limit))

    filters.append(partial(in_category, categories=filter_args['category']))
    filters.append(partial(in_size, sizes=filter_args['size']))
    filters.append(partial(in_condition, conditions=filter_args['condition']))
    filters.append(partial(in_watchnext_price, prices=filter_args['price'], feature_user_ids=CONST_MAP.feature_user_id))
    filters.append(partial(gender, gender_ids=filter_args['sex']))
    # if 'keep_sold_post' not in filter_args:
    #     filters.append(avoid_sold_post)
    if len(CONST_MAP.avoid_user_id) > 0:
        filters.append(partial(avoid_user, user_ids=CONST_MAP.avoid_user_id))
    filters.append(partial(avoid_banned_post, user_id=filter_args['user_id']))
    # TODO fix tuple(shop_ids) , order_cols=[f'user_id in {tuple(shop_ids)}'], direction=['desc']
    filters.append(partial(add_order_top_posts))
    post_infos = eligible_post_source(filters)
    return post_infos