import math
import logging
import random

from src.const import const_map as CONST_MAP
from src.common.post_info_class import PostInfo
from src.common.random_shuffle import random_post_info_shuffle
from src.recommendation.utils.scoring import get_final_score
from src.recommendation.filter.new_filter import filter_post, non_db_filter
from src.recommendation.source.dashboard_source import dashboard_creation

from src.utils.db_utils import execute_raw_query
from src.utils.redis_utils import insert_to_list_key
from src.utils.query.user_history import get_user_all_like_dislike_post
from src.utils.exception import DBError, FaissIndexError
from src.utils.decorator import log_func_time
from src.utils.redis_caching import redis_cache_value, redis_cache_list, redis_cache_json

from src.carousel.watchnext_post import *

deviation_logger = logging.getLogger('deviation_logger')
work_logger = logging.getLogger('work_logger')


@log_func_time
def matching_user_with_content(user_id:int, number_of_recommend:int, request_type:str, filter_args:dict) -> list[int]:
    try:
        # tranform request_type into subsets of post segmentations
        source_order, source_number, filter_args = transform_input_param(user_id, number_of_recommend, request_type, filter_args)
        
        # building decks of posts
        source_post = create_source_post(source_order, user_id, request_type, filter_args)

        # dedup posts from sources
        matched_results = all_source_addition(source_order, source_post, source_number, number_of_recommend, user_id)

        # limit 1 shop posts
        matched_results = single_shop_post_limit_after_combine(matched_results)
        
        if check_last_login_condition(user_id):
            dashboard_result = dashboard_creation()
            dashboard_result = non_db_filter(dashboard_result, {'user_id': user_id})
            work_logger.info('User: %s. Dashboard source: %s' % (user_id, dashboard_result))
            random.shuffle(matched_results)
            matched_results = dashboard_result + matched_results
        final_results = clean_up(matched_results, user_id, number_of_recommend)
        return final_results 
    except Exception as e:
        deviation_logger.error('Recommendation deviation: %s' % e, exc_info=True)
        return []


@redis_cache_json(key_maker=lambda discovery_type: 'discovery_%s' % discovery_type, expire_secs=1800)
def matching_user_with_content_redis(discovery_type='trending') -> list[int]:
    try:
        if discovery_type == 'trending':
            pass
        elif discovery_type == 'curating':
            pass
        elif discovery_type == 'personalize':
            pass
        elif discovery_type == 'mall':
            pass
        elif discovery_type == '2hand':
            pass
        elif discovery_type == 'new':
            pass
        else:
            raise 'Unsupported Discovery Type..'
        
        query = '''
        select id 
        from top_posts tp
        where 1=1
        and tp.gender_id in :gender_id
        and tp.total_views >= :view_limit
        and tp.total_favorites >= :like_limit
        order by score desc
        '''
        res_male = execute_raw_query(query, gender_id=tuple([1]), view_limit=30, like_limit=3)
        final_results_male = [int(i[0]) for i in res_male]

        res_female = execute_raw_query(query, gender_id=tuple([2,3]), view_limit=30, like_limit=3)
        final_results_female = [int(i[0]) for i in res_female]

        final_results = [final_results_male, final_results_female]

        return final_results 
    except Exception as e:
        deviation_logger.error('Redis cache content Error for Discovery %s: %s' % (discovery_type, e), exc_info=True)
        return []


@log_func_time
def check_last_login_condition(user_id:int) -> bool:
    query = '''
    select date_part('hour',current_timestamp - max(t2.created_at))
    from tracing t2
    where t2."action" = 'view'
    and t2.actor_id = :user_id
    '''
    res = execute_raw_query(query, user_id=user_id)
    try:
        hour_distance = int(res[0][0])
    except Exception as e:
        return True
    if hour_distance >= CONST_MAP.dashboard_time_threshold:
        return True
    return False


# @log_func_time
def transform_input_param(user_id:int, number_of_recommend:int, request_type:str, filter_args:dict) -> tuple[list[str], list[int], dict]:
    filter_args['time_limit']=CONST_MAP.time_limit_medium

    #
    if request_type == 'manual_curating':
        source_order = CONST_MAP.source_order_manual_curating
        source_ratio = CONST_MAP.source_ratio_manual_curating
        filter_args['time_limit']=CONST_MAP.manual_curating_time_limit

    #
    elif request_type == 'manual_select_keyword':
        source_order = CONST_MAP.source_order_trending
        source_ratio = CONST_MAP.source_ratio_trending
        filter_args['have_keyword'] = CONST_MAP.manual_select_keyword

    #
    elif request_type == 'personalize':
        user_history = get_user_all_like_dislike_post(user_id)
        filter_args['time_limit']=CONST_MAP.discovery_4you_time_limit
        if len(user_history) >= CONST_MAP.cold_start_threshold:
            source_order = CONST_MAP.source_order_personalize
            source_ratio = CONST_MAP.source_ratio_personalize
        else:
            source_order = CONST_MAP.source_order_coldstart
            source_ratio = CONST_MAP.source_ratio_coldstart
    
    # discovery 2hand
    elif request_type == 'discovery_2hand':
        source_order = CONST_MAP.source_order_2hand
        source_ratio = CONST_MAP.source_ratio_mall
    # discovery new
    elif request_type == 'discovery_new':
        source_order = CONST_MAP.source_order_new
        source_ratio = CONST_MAP.source_ratio_mall
    # discovery mall
    elif request_type == 'discovery_mall':
        source_order = CONST_MAP.source_order_mall
        source_ratio = CONST_MAP.source_ratio_mall
    # placeholder
    else:
        source_order = CONST_MAP.source_order_trending
        source_ratio = CONST_MAP.source_ratio_trending
        filter_args['keep_sold_post'] = True

    # distributing post based on ratio
    real_order:list[str] = []
    real_ratio:list[float] = []
    for source, ratio in zip(source_order, source_ratio):
        if ratio > 0:
            real_order.append(source)
            real_ratio.append(ratio)
    
    # distributing
    post_number_scale_ratio = 1.0/sum(real_ratio)
    number_list = [math.ceil(number_of_recommend * ratio * post_number_scale_ratio) for ratio in real_ratio]

    # resulting
    return real_order, number_list, filter_args

'''
This is to create a list of post from various decks.
Deck: a colelction of posts pulled over a set of logic

'''
def create_source_post(source_order:list[str], user_id:int, request_type:str, filter_args:dict) -> dict[str, list[PostInfo]]:
    source_post_raw = {}

    #https://docs.google.com/document/d/17o-hdzgiJu7tbmAQkhuj2StITHactcaXtYmQG9ii26g/edit#heading=h.gn14wqje50rt
    for source in source_order:
        if source == 'shop': # unchecked by andy
            source_post_raw[source] = get_shop_post_info(filter_args, request_type, user_id)
        elif source == 'popular_business': # unchecked by andy
            source_post_raw[source] = get_popular_business_post_info(filter_args)
        elif source == 'popular': # unchecked by andy
            source_post_raw[source] = get_popular_post_info(filter_args)
        elif source == 'featured': # unchecked by andy
            source_post_raw[source] = get_featured_post_info(filter_args)
        elif source == 'recsys': # unchecked by andy
            source_post_raw['recsys'] = get_recsys_post_info(user_id, filter_args)
        elif source == 'following': # unchecked by andy
            source_post_raw['following'] = get_following_post_info(user_id, filter_args)
        elif source == 'newpost': # unchecked by andy
            source_post_raw[source] = get_newpost_info(filter_args)
        elif source == 'new_2hand': # unchecked by andy
            source_post_raw[source] = get_newpost_2hand_info(filter_args)
        elif source == 'discovery_mall':
            source_post_raw[source] = get_mall_post_info(filter_args)
        elif source == 'discovery_2hand':
            source_post_raw[source] = get_2hand_post_info(filter_args)
        elif source == 'discovery_new':
            source_post_raw[source] = get_new_post_info(filter_args)
        elif source == 'brand_mall':
            source_post_raw[source] = get_brand_mall_post_info(filter_args)
        elif source == 'remind':
            source_post_raw[source] = get_remind_source(filter_args)
        elif source == 'curator':
            source_post_raw[source] = get_curator_source(filter_args)

    source_post_score = filter_post(user_id, source_post_raw, filter_args)
    # source_post_score = get_final_score(user_id, source_post_score, 100)
    source_post = {}
    for source in source_order:
        source_post[source] = random_post_info_shuffle(source_post_score[source])
    return source_post


# @log_func_time
def all_source_addition(source_order:list[str], source_post:dict[str, list[PostInfo]], source_number:list[int], number_of_recommend:int, user_id:int) -> list[int]:
    matched_results:list[int] = []
    work_logger.info('User: %s. First fill:' % user_id)
    for i in range(len(source_order)):
        matched_results = single_source_addition(source_order[i], source_post, source_number[i], matched_results, user_id)
    work_logger.info('User: %s. Missing fill:' % user_id)
    for i in range(len(source_order)):
        matched_results = single_source_addition(source_order[i], source_post, number_of_recommend*10 - len(matched_results), matched_results, user_id)
    return matched_results


def single_source_addition(source:str, source_post:dict[str, list[PostInfo]], number:int, current_result:list[int], user_id:int) -> list[int]:
    non_duplicate_post = [post_info.pid for post_info in source_post[source] if post_info.pid not in current_result]
    work_logger.info('User: %s. %s posts: %s' % (user_id, source, str(non_duplicate_post[:number])))
    current_result += non_duplicate_post[:number]
    work_logger.info('User: %s. After %s posts: %s' % (user_id, source, current_result))
    return current_result


def single_shop_post_limit_after_combine(matched_results:list[int]) -> list[int]:
    if len(matched_results) < 1:
        return matched_results
    shop_query = '''
    select p.id, p.user_id 
    from post p 
    where p.id in :post_ids
    '''
    res = execute_raw_query(shop_query, post_ids=tuple(matched_results))
    shop_ids = {int(p):int(s) if s is not None else -1 for p,s in res}
    filtered_post_ids = []
    shop_counter = {}
    for pid in matched_results:
        sid = shop_ids[pid]
        if sid == -1:
            continue
        if sid not in shop_counter:
            shop_counter[sid] = 0
        shop_counter[sid] += 1
        if shop_counter[sid] < 5:
            filtered_post_ids.append(pid)
    return filtered_post_ids


def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]


# @log_func_time
def clean_up(matched_results:list[int], user_id:int, number_of_recommend:int) -> list[int]:
    matched_results = remove_values_from_list(matched_results, -1)
    if len(matched_results) == 0:
        return []
        
    matched_results = matched_results[:number_of_recommend]
    random.shuffle(matched_results)
    work_logger.info('User: %s. Final posts: %s' % (user_id, matched_results))
    if len(matched_results) < number_of_recommend:
        deviation_logger.info('User: %s. Recommendation deviation: not enough recommend post' % user_id)
    insert_to_list_key(key='uid:recommended:%s' % user_id, values=matched_results, expire=CONST_MAP.latest_history_expire_day * 86400, trim_limit=CONST_MAP.avoid_history_trim_limit)
    return matched_results 