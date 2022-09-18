from numpy import e
from src.common.post_info_class import PostInfo
from src.utils.db_utils import execute_raw_query
from src.utils.redis_utils import get_viewed_post
from typing import List, Tuple, Dict, Any, Union
from src.const import const_map as CONST_MAP
from src.utils.decorator import log_func_time
from src.utils.exception import InputError

import logging
work_logger = logging.getLogger('work_logger')
@log_func_time
def filter_post(user_id:int, source_map:dict[str, list[PostInfo]], filter_args:dict[str, Any]) -> dict[str, list[PostInfo]]:
    if 'no_filter' in filter_args and filter_args['no_filter'] == True:
        return source_map
    total_ids_set = total_ids_set_creation(user_id, source_map)

    total_ids = non_db_filter(list(total_ids_set), filter_args)
    work_logger.info('User: %s. Remain legit ids after non db filter: %s' % (user_id, total_ids))
    total_legit_ids = total_ids
    # total_legit_ids = db_filter(total_ids, filter_args)
    # work_logger.info('User: %s. Remain legit ids after db filter: %s' % (user_id, total_legit_ids))
    for source in source_map:
        source_map[source] = [post_info for post_info in source_map[source] if post_info.pid in total_legit_ids]
        work_logger.info('User: %s. Remain legit in source %s: Ids %s' % (user_id, source, source_map[source]))

    return source_map

# @log_func_time
def total_ids_set_creation(user_id:int, source_map:dict[str, list[PostInfo]]):
    total_ids_set = set()
    for source in source_map:
        result_ids = [post_info.pid for post_info in source_map[source]]
        work_logger.info('User: %s. Source %s. Ids: %s' % (user_id, source, result_ids))
        total_ids_set |= set(result_ids)
        work_logger.info('User: %s. Append source: Total_ids: %s' % (user_id, total_ids_set))
    return total_ids_set

@log_func_time
def non_db_filter(candidate_post_ids: list[int], filter_args:dict[str, Any]) -> list[int]:
    if len(candidate_post_ids) > 0:
        if 'user_id' in filter_args:
            user_id = filter_args['user_id']
            avoid_post_ids = get_viewed_post(user_id)
            work_logger.info('User: %s. Avoid posts: %s' % (user_id, avoid_post_ids)) 
            candidate_post_ids = [i for i in candidate_post_ids if i not in avoid_post_ids]
    return candidate_post_ids

@log_func_time
def db_filter(candidate_post_ids: list[int], filter_args:dict[str, Any]) -> list[int]:
    if len(candidate_post_ids) > 0:
        kwargs = {'candidate_ids':tuple(candidate_post_ids)}
        base_query = '''
        select distinct p.id
        from post p
        where p.id in :candidate_ids
        '''
        
        base_query, kwargs = db_category_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_size_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_condition_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_price_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_sex_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_const_avoid_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_delete_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_sold_post_filter(base_query, filter_args, kwargs)
        base_query, kwargs = db_banned_post_filter(base_query, filter_args, kwargs)
        
        res = execute_raw_query(base_query, **kwargs)
        candidate_post_ids = [i[0] for i in res]
        return candidate_post_ids
    else:
        return candidate_post_ids

def db_category_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'category' in filter_args and len(filter_args['category']) > 0:
        base_query += ''' and p.category_id in :accepted_categories'''# % ','.join([str(i) for i in filter_args['category']])
        query_kwargs['accepted_categories'] = tuple(filter_args['category'])
    return base_query, query_kwargs

def db_size_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'size' in filter_args and len(filter_args['size']) > 0:
        base_query += ''' and p.size_id in :accepted_sizes''' # % ','.join([str(i) for i in filter_args['size']])
        query_kwargs['accepted_sizes'] = tuple(filter_args['size'])
    return base_query, query_kwargs

def db_condition_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'condition' in filter_args and len(filter_args['condition']) > 0:
        base_query += ''' and p.condition_id in :accepted_conditions''' # % ','.join([str(i) for i in filter_args['condition']])
        query_kwargs['accepted_conditions'] = tuple(filter_args['condition'])
    return base_query, query_kwargs

def db_price_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'price' in filter_args and len(filter_args['price']) == 2:
        base_query += ''' and ((p.amount >= :low_price and p.amount <= :high_price) or p.user_id in :featured_user_ids)''' # % (str(filter_args['price'][0]), str(filter_args['price'][1]))
        query_kwargs['low_price'] = filter_args['price'][0]
        query_kwargs['high_price'] = filter_args['price'][1]
        query_kwargs['featured_user_ids'] = tuple(CONST_MAP.feature_user_id)
    return base_query, query_kwargs

def db_sex_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'sex' in filter_args and len(filter_args['sex']) > 0:
        base_query += ''' and p.gender_id in :accepted_sexes''' # % ','.join([str(i) for i in filter_args['sex']])
        query_kwargs['accepted_sexes'] = tuple(filter_args['sex'])
    return base_query, query_kwargs

def db_const_avoid_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if len(CONST_MAP.avoid_user_id) > 0:
        base_query += ''' and p.user_id not in (%s)''' % ','.join([str(i) for i in CONST_MAP.avoid_user_id])
    return base_query, query_kwargs

def db_delete_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'keep_deleted_post' not in filter_args or filter_args['keep_deleted_post'] == False:
        base_query += ''' and p.is_deleted = false and p.is_public = true'''
    return base_query, query_kwargs

def db_sold_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'keep_sold_post' not in filter_args or filter_args['keep_sold_post'] == False:
        base_query += ''' and p.is_sold = false and p.is_for_sale =true'''
    return base_query, query_kwargs

def db_banned_post_filter(base_query:str, filter_args:dict[str, Any], query_kwargs:dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if 'keep_banned_post' not in filter_args or filter_args['keep_banned_post'] == False:
        if 'user_id' in filter_args:
            if type(filter_args['user_id']) != int:
                raise InputError('Filter banned post: require int user_id filed, get %s' % str(filter_args))
            base_query += ''' and p.id not in (
select CAST (rl.object_id as int)
from reporting_log rl
where rl.reported_by_id = :user_id
and rl.object_type_id = 17
) and
p.user_id not in (
select CAST (rl.object_id as int)
from reporting_log rl
where rl.reported_by_id = :user_id
and rl.object_type_id = 6)
and p.user_id not in (
select b.user_id
from blocking b
where b.blocked_by = :user_id)
'''
            query_kwargs['user_id'] = filter_args['user_id']
    return base_query, query_kwargs