from src.common.current_time import get_query_time_str
from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP
from src.utils.redis_utils import insert_and_trim
from src.utils.db_utils import execute_raw_query
from src.utils.decorator import log_func_time
from typing import Tuple, List, Dict

import logging
deviation_logger = logging.getLogger('deviation_logger')

def get_user_all_like_dislike_post(user_id:int) -> List[int]:
    keys = ['uid:like:%s' % user_id, 'uid:dislike:%s' % user_id]
    max_expire_time = CONST_MAP.latest_history_expire_day * 86400
    for key in keys:
        if max_expire_time - RESOURCE_MAP['redis_conn'].ttl(key) > 30:
            refresh_long_history(user_id)
            break
    liked_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:like:%s' % user_id, -300, -1) if int(i) > 0]
    disliked_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:dislike:%s' % user_id, -300, -1) if int(i) > 0]
    return liked_ids + disliked_ids

@log_func_time
def get_latest_history(user_id:int) -> Tuple[List[int], List[int], List[float], List[float]]:
    keys = ['uid:like:%s' % user_id, 'uid:dislike:%s' % user_id, 'uid_time:like:%s' % user_id, 'uid_time:dislike:%s' % user_id]
    max_expire_time = CONST_MAP.latest_history_expire_day * 86400
    for key in keys:
        if max_expire_time - RESOURCE_MAP['redis_conn'].ttl(key) > 60:
            refresh_long_history(user_id)
            break
    liked_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:like:%s' % user_id, 0, CONST_MAP.latest_history_threshold)]
    disliked_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:dislike:%s' % user_id, 0, CONST_MAP.latest_history_threshold)]
    liked_times = [float(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid_time:like:%s' % user_id, 0, CONST_MAP.latest_history_threshold)]
    disliked_times = [float(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid_time:dislike:%s' % user_id, 0, CONST_MAP.latest_history_threshold)]
    return liked_ids, disliked_ids, liked_times, disliked_times

@log_func_time
def refresh_long_history(user_id:int) -> None:
    query = '''
    (
    with prun_tracing as (
        select action, actor_id, object_id::int, max(t.created_at) as created_at
        from tracing t left join post p on p.id = t.object_id::int
        where t.created_at > current_date - interval '1 month' 
        and t.actor_id != p.user_id
        and t.actor_id = :user_id
        group by 1, 2, 3
        --    limit 100
    ),
    like_dislike as (
        ( -- dislike: ignore and unlike
            select distinct object_id, 'dislike' as status, -1 as score, tr.created_at 
            from prun_tracing tr
            where tr.actor_id = :user_id
            and "action" in ('ignore')
            order by tr.created_at desc
            limit 5
        ) union ( -- see more or interested in
            select distinct object_id, 'like' as status, 0.5 as score, tr.created_at 
            from prun_tracing tr
            where ("action" in (
                    'onboarding_select_styles_ref_post', 'search_result_click_post', 'search_home_hashtag_click_post'
                ) or (
                    action like '%%popup%%'
                )    
            )
            order by tr.created_at desc
            limit 5
        ) union ( -- like, share or buy intent
            select distinct object_id, 'like' as status, 1.0 as score, tr.created_at 
            from prun_tracing tr
            where ("action" in (
                    'like', 'share',
                    'post_inside_popup_add_cart', 'cart_click_buy_item'
                ) or (
                    action like '%%buy%%'
                )    
            )
            order by tr.created_at desc
            limit 5
        )
    )
    select ld.object_id::int as post_id, ld.status, ld.score, ld.created_at as time
    from like_dislike ld 
    ) union 
    -- reported post 
    (
    select rl.object_id::int as post_id, 'dislike' as status, -1.0 as score, rl.created_at as time
    from reporting_log rl 
    where rl.reported_by_id = :user_id
    and object_type_id = 17
    and rl.created_at > current_date - interval '1 month' 
    limit 3
    )

    ''' #% get_query_time_str()
    res = execute_raw_query(query, user_id=user_id)#, 
                                    # pos_thres=CONST_MAP.history_min_like_time, 
                                    # neg_thres=CONST_MAP.history_max_dislike_time, 
                                    # noise_thres=CONST_MAP.history_max_like_time)
    liked_ids = []
    liked_times = []
    disliked_ids = []
    disliked_times = []
    for tup in res:
        if tup[0] is None:
            continue
        try:
            event_view_time_score = float(tup[2])
        except TypeError as e:
            deviation_logger.error('User: %s. History time convert error: %s' % (user_id, tup[1]), exc_info=True)
            event_view_time_score =  0.0

        if tup[1] == 'like':
            liked_ids.append(int(tup[0]))
            liked_times.append(event_view_time_score)
        elif tup[1] == 'dislike':
            disliked_ids.append(int(tup[0]))
            disliked_times.append(event_view_time_score)
    if isinstance(CONST_MAP.latest_history_expire_day, int):
        insert_and_trim('uid:like:%s' % user_id, liked_ids, 'uid_time:like:%s' % user_id, liked_times,
            expire_secs = CONST_MAP.latest_history_expire_day * 86400, trim_limit=50)
        insert_and_trim('uid:dislike:%s' % user_id, disliked_ids, 'uid_time:dislike:%s' % user_id, disliked_times,
            expire_secs = CONST_MAP.latest_history_expire_day * 86400, trim_limit=50)
    else:
        raise RuntimeError('Config type error: latest_history_expire_day require int, get %s' % CONST_MAP.latest_history_expire_day)
