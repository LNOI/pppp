import random

from src.carousel.watchnext_post import get_popular_post_info
from src.recommendation.filter.new_filter import non_db_filter, db_filter
from src.utils.redis_utils import insert_to_list_key
from src.utils.db_utils import execute_raw_query
from src.common.current_time import get_query_time_str
from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP


def placeholder_watchnext(user_id:int, number_of_recommend:int) -> list[int]:
    post_ids, raw_scores = get_popular_post_info(None)
    filtered_post_ids = non_db_filter(post_ids, {'user_id':user_id})
    if len(filtered_post_ids) > 0:
        random.shuffle(filtered_post_ids)
        selected_post_ids = filtered_post_ids[:number_of_recommend]
        insert_to_list_key(key='uid:recommended:%s' % user_id, values=selected_post_ids, expire=CONST_MAP.latest_history_expire_day * 86400, trim_limit=1000)
        return selected_post_ids
    else:
        return []


def dummy_result():
    print('outer_placeholder')
    post_ids = query_simple_popular_post()
    random.shuffle(post_ids)
    return post_ids


def trend_placeholder(user_id:int, number_of_recommend:int, filter_args):
    post_ids, raw_scores = get_popular_post_info(None)
    filtered_post_ids = non_db_filter(post_ids, filter_args)
    filtered_post_ids = db_filter(filtered_post_ids, filter_args)
    if len(filtered_post_ids) > 0:
        random.shuffle(filtered_post_ids)
        selected_post_ids = filtered_post_ids[:number_of_recommend]
        insert_to_list_key(key='uid:recommended:%s' % user_id, values=selected_post_ids, expire=CONST_MAP.latest_history_expire_day * 86400, trim_limit=1000)
        return selected_post_ids
    else:
        return dummy_result()


def foryou_placeholder(user_id:int, number_of_recommend:int, filter_args):
    avoid_user_id = CONST_MAP.avoid_user_id + [3]
    avoid_user_str = ','.join([str(i) for i in avoid_user_id])
    
    shop_query = '''
    select p.id from top_posts p join top_sellers au on p.user_id = au.id
    where au.is_business_acc = true 
    and p.is_sold  = false 
    and au.id not in (%s)
    order by p.created_at desc
    limit :limit
    ''' % avoid_user_str
    
    res = execute_raw_query(shop_query, limit=300)
    shop_post_ids = [int(i[0]) for i in res]
    
    filtered_post_ids = non_db_filter(shop_post_ids, filter_args)
    filtered_post_ids = db_filter(filtered_post_ids, filter_args)
    if len(filtered_post_ids) > 0:
        random.shuffle(filtered_post_ids)
        selected_post_ids = filtered_post_ids[:number_of_recommend]
        insert_to_list_key(key='uid:recommended:%s' % user_id, values=selected_post_ids, expire=CONST_MAP.latest_history_expire_day * 86400, trim_limit=1000)
        return selected_post_ids
    else:
        return dummy_result()


def query_simple_popular_post():
    avoid_curating_condition = ''
    if isinstance(CONST_MAP.feature_user_id, list) and len(CONST_MAP.feature_user_id) > 0:
        avoid_curating_condition = ' and p.user_id not in (%s)' % ','.join([str(i) for i in CONST_MAP.feature_user_id])
    query = '''
    select p.id
    from top_posts p
    where p.total_favorites >= 5
    and p.created_at > %s - interval '30 days' 
    %s
    limit 500
    ''' % (get_query_time_str(), avoid_curating_condition)
    
    query_result = execute_raw_query(query)
    
    if len(query_result) > 0:
        post_ids = [int(item[0]) for item in query_result]
    else:
        post_ids = []
    return post_ids


def filter_placeholder(user_id:int, number_of_recommend:int, filter_args):
    query = '''
    with placeholder as (
        select p.id, (p.ai_metadata->'post_score'->'total')::float as score
        from eligible_posts p
        where 1=1  
        and p.gender_id in :gender_id
        and p.created_at > current_date - interval '30 days'
    )
    select id
    from placeholder
    where score is not null
    order by random() * score desc
    limit %d
    ''' % (number_of_recommend)
    
    if filter_args['sex'] == []:
        filter_args['sex'] = [1,2,3]

    res = execute_raw_query(query, gender_id=tuple(filter_args['sex']))
    ids = [int(item[0]) for item in res]
    # removal
    '''
    filtered_post_ids = non_db_filter(ids, filter_args)
    filtered_post_ids = db_filter(filtered_post_ids, filter_args)
    if len(filtered_post_ids) > 0:
        random.shuffle(filtered_post_ids)
        selected_post_ids = filtered_post_ids[:number_of_recommend]
    else:
        random.shuffle(ids)
        selected_post_ids = ids[:number_of_recommend]
    insert_to_list_key(key='uid:recommended:%s' % user_id, values=selected_post_ids, expire=CONST_MAP.latest_history_expire_day * 86400, trim_limit=1000)
    '''
    return ids

def static_placeholder():
    return random.sample(RESOURCE_MAP['placeholder_post_ids'], 50)