import enum
from re import I
from typing import Any, Optional
from src.utils.db_utils import execute_raw_query
from src.utils.redis_caching import set_redis_json_value, get_redis_json_value
from src.const.global_map import RESOURCE_MAP
from src.const import const_map as CONST_MAP
class TimeDuration(enum.Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    def __str__(self):
        return self.value
def get_leaderboard_result(user_id:int, live_hour:int=24) -> dict[str, Any]:
    redis_key = 'leaderboard_v4'
    result_lists = refresh_leaderboard_info_cache(live_hour)
    old_leaderboard_result = None
    ttl = RESOURCE_MAP['redis_conn'].ttl(redis_key)
    if ttl >= -1:
        old_leaderboard_result = get_redis_json_value(redis_key)
    if ttl > 3600*(live_hour-1):
        new_leaderboard_result = old_leaderboard_result
    else:
        new_leaderboard_result = {
            'period':['Tuần', 'Tháng'],
            'title':[],
            'data':[]
        }
        shop_title, shop_data_map = get_shop_leaderboard_result(old_leaderboard_result, CONST_MAP.leaderboard_size, result_lists)
        new_leaderboard_result['title'].append(shop_title)
        new_leaderboard_result['data'].append(shop_data_map)
        post_title, post_data_map = get_post_leaderboard_result(old_leaderboard_result, CONST_MAP.leaderboard_size, result_lists)
        new_leaderboard_result['title'].append(post_title)
        new_leaderboard_result['data'].append(post_data_map)
        # event_title, event_data_map = get_event_leaderboard_result(old_leaderboard_result, CONST_MAP.leaderboard_size, result_lists)
        # new_leaderboard_result['title'].append(event_title)
        # new_leaderboard_result['data'].append(event_data_map)
        set_redis_json_value(new_leaderboard_result, redis_key, 3600*live_hour)
    
    add_user_rank_to_leaderboard_result(user_id, new_leaderboard_result, result_lists)
    return new_leaderboard_result

def get_post(duration:TimeDuration):
    query = '''
    with ranking_table as (
        select w.post_id, count(*) as score, max(p.caption) as caption, max(p.user_id) as user_id
        from wishlist w left join post p on p.id = w.post_id 
        --where w.created_at > current_date
        where w.created_at > date_trunc(:duration, current_date)
        and p.is_sold = false 
        and p.created_at > date_trunc(:duration, current_date) - ('1 '||:duration)::interval
        and p.user_id not in (
            select id 
            from account_user
            where account_level_id in (2, 99)
        )
        group by w.post_id
        order by score desc
    ),
    temp_table as (
        select user_id, max(score) as max_score
        from ranking_table
        group by user_id
        order by max_score desc
    )
    select tt.user_id, max(rt.post_id) as post_id, max(rt.score) as score
    from temp_table tt left join ranking_table rt on tt.max_score = rt.score and tt.user_id = rt.user_id
    group by tt.user_id
    order by score desc
    limit :limit
    '''
    res = execute_raw_query(query, duration=str(duration), limit=CONST_MAP.leaderboard_size)
    post_res = [{
        'user_id':int(uid),
        'post_id':int(pid),
        'score':float(score),
        'rank':i
    } for i, (uid, pid, score) in enumerate(res)
    ]
    return post_res

def get_shop(duration:TimeDuration):
    query = '''
    select af.user_id, count(distinct af.followed_by) as follow_count
    from account_following af
    left join top_sellers au on af.user_id = au.id
    where af.created_at > date_trunc(:duration, current_date)
    and au.account_level_id not in (2, 99)
    group by af.user_id
    order by follow_count desc
    '''
    res = execute_raw_query(query, duration=str(duration))
    shop_res = [{
        'user_id':uid,
        'follow_count':follow_count
    } for uid, follow_count in res
    ]
    return shop_res

def get_event_user(duration:TimeDuration):
    if duration == TimeDuration.MONTH:
        query = '''
    with event_week_point as ( select ll.user_id, ll.points, (ll."data" ->'event')::text as event_text, ll."timestamp" as ts from loyalty_loyaltyhistory ll 
        where true 
        and ll."timestamp" > now() - '30 day'::interval - ('3 hour')::interval
        and ll.verb = 'general'),
    score_table as  (  select e.user_id, sum(e.points) as point from event_week_point e
        where e.event_text = '"LEADERBOARD"'
        group by e.user_id 
        order by sum(e.points) desc, max(e.ts) asc)
    select st.* from score_table st join account_user au on st.user_id=au.id
    where au.is_business_acc = false '''
    else:
        query = '''
    with event_week_point as ( select ll.user_id, ll.points, (ll."data" ->'event')::text as event_text, ll."timestamp" as ts from loyalty_loyaltyhistory ll 
        where true 
        and ll."timestamp" > date_trunc(:duration, current_date) - ('3 hour')::interval
        and ll.verb = 'general'),
    score_table as  (  select e.user_id, sum(e.points) as point from event_week_point e
        where e.event_text = '"LEADERBOARD"'
        group by e.user_id 
        order by sum(e.points) desc, max(e.ts) asc)
    select st.* from score_table st join account_user au on st.user_id=au.id
    where au.is_business_acc = false '''
    res = execute_raw_query(query, duration=str(duration))
    event_user_res = [
        {
            'user_id':int(item[0]),
            'point':int(item[1])
        } for item in res
    ]
    return event_user_res

def refresh_leaderboard_info_cache(live_hour:int):
    week_post_rank_key, month_post_rank_key = 'leaderboard:user_post:week', 'leaderboard:user_post:month'
    week_shop_rank_key, month_shop_rank_key = 'leaderboard:shop:week', 'leaderboard:shop:month'
    week_event_rank_key, month_event_rank_key = 'leaderboard:event:week', 'leaderboard:event:month'
    ttl = RESOURCE_MAP['redis_conn'].ttl(week_event_rank_key)  # one key logic represent 4 keys similar logic
    if ttl < 3600*(live_hour-1): # non exist key ttl is -2, permenent key ttl is -1, both also need refresh
        shop_week_list = get_shop(TimeDuration.WEEK)
        shop_month_list = get_shop(TimeDuration.MONTH)
        post_week_list = get_post(TimeDuration.WEEK)
        post_month_list = get_post(TimeDuration.MONTH)
        event_user_week_list = get_event_user(TimeDuration.WEEK)
        event_user_month_list = get_event_user(TimeDuration.MONTH)
        set_redis_json_value(post_week_list, week_post_rank_key, 3600*live_hour)
        set_redis_json_value(post_month_list, month_post_rank_key, 3600*live_hour)
        set_redis_json_value(shop_week_list, week_shop_rank_key, 3600*live_hour)
        set_redis_json_value(shop_month_list, month_shop_rank_key, 3600*live_hour)
        set_redis_json_value(event_user_week_list, week_event_rank_key, 3600*live_hour)
        set_redis_json_value(event_user_month_list, month_event_rank_key, 3600*live_hour)
    else:
        shop_week_list = get_redis_json_value(week_shop_rank_key)
        shop_month_list = get_redis_json_value(month_shop_rank_key)
        post_week_list = get_redis_json_value(week_post_rank_key)
        post_month_list = get_redis_json_value(month_post_rank_key)
        event_user_week_list = get_redis_json_value(week_event_rank_key)
        event_user_month_list = get_redis_json_value(month_event_rank_key)
    return shop_week_list, shop_month_list, post_week_list, post_month_list, event_user_week_list, event_user_month_list

def add_user_rank_to_leaderboard_result(user_id: int, leaderboard_result:dict[str, Any], result_lists:tuple[list]):
    shop_week_list, shop_month_list, post_week_list, post_month_list, event_user_week_list, event_user_month_list = result_lists
    for period in ['Tuần', 'Tháng']:
        post_list = post_week_list if period == 'Tuần' else post_month_list
        shop_list = shop_week_list if period == 'Tuần' else shop_month_list

        shop_rank = len(shop_list)
        for index in range(len(shop_list)):
            if user_id == shop_list[index]['user_id']:
                shop_rank = index
                break
        leaderboard_result['data'][0][period]['user'] = {
           'rank': shop_rank
        }

        leaderboard_result['data'][1][period]['user'] = {
            'post_id':None,
            'rank': len(post_list)
        }
        for index in range(len(post_list)):
            if user_id == post_list[index]['user_id']:
                leaderboard_result['data'][1][period]['user'] = {
                    'post_id':post_list[index]['post_id'],
                    'rank': post_list[index]['rank']
                }
                break
        del leaderboard_result['data'][1][period]['shop_ids']

        # if user_id in CONST_MAP.home_api_test_user:
        event_user_list = event_user_week_list if period == 'Tuần' else event_user_month_list
        event_rank = len(event_user_list)
        for index in range(len(event_user_list)):
            if user_id == event_user_list[index]['user_id']:
                event_rank = index
                break
        # leaderboard_result['data'][2][period]['user'] = {
        # 'rank': event_rank
        # }

def get_shop_leaderboard_result(old_leaderboard_result:Optional[dict[str, Any]], leaderboard_size, result_lists:tuple[list]):
    shop_week_list, shop_month_list, post_week_list, post_month_list, event_user_week_list, event_user_month_list = result_lists
    title = CONST_MAP.leaderboard_titles[0]
    content = 'Top %s shop có lượt follow tăng nhanh'
    data_map = {}
    for period in ['Tuần', 'Tháng']:
        shop_list = shop_week_list if period == 'Tuần' else shop_month_list
        
        if old_leaderboard_result is None:
            old_shop_order = [None] * leaderboard_size
        else:
            old_shop_order = old_leaderboard_result['data'][0][period]['ids']

        new_shop_order = [item['user_id'] for item in shop_list][:leaderboard_size]
        new_shop_score = [item['follow_count'] for item in shop_list][:leaderboard_size]
        change_shop_rank = [(new_shop_order.index(iid) - old_shop_order.index(iid))
                            if iid in old_shop_order else leaderboard_size
                            for iid in new_shop_order][:leaderboard_size]

        data_map[period] = {
            'type':'user_account',
            'title':title,
            'content':content % len(new_shop_order),
            'ids':new_shop_order,
            'rank_change':change_shop_rank,
            'score':new_shop_score
        }

    return title, data_map

def get_post_leaderboard_result(old_leaderboard_result:Optional[dict[str, Any]], leaderboard_size, result_lists:tuple[list]):
    shop_week_list, shop_month_list, post_week_list, post_month_list, event_user_week_list, event_user_month_list = result_lists
    title = CONST_MAP.leaderboard_titles[1]
    content = 'Top %s bài đăng có lượt like tăng nhanh'
    data_map = {}
    for period in ['Tuần', 'Tháng']:
        post_list = post_week_list if period == 'Tuần' else post_month_list
        
        if old_leaderboard_result is None:
            old_post_order = [None] * leaderboard_size
        else:
            old_post_order = old_leaderboard_result['data'][1][period]['ids']
        
        new_post_user = [item['user_id'] for item in post_list][:leaderboard_size]
        new_post_order = [item['post_id'] for item in post_list][:leaderboard_size]
        new_post_score = [item['score'] for item in post_list][:leaderboard_size]
        change_post_rank = [(new_post_order.index(iid) - old_post_order.index(iid))
                            if iid in old_post_order else leaderboard_size
                            for iid in new_post_order][:leaderboard_size]
        
        data_map[period] = {
            'type':'post',
            'title':title,
            'content':content % len(new_post_order),
            'ids':new_post_order,
            'rank_change':change_post_rank,
            'score':new_post_score,
            'shop_ids':new_post_user
        }

    return title, data_map

def get_event_leaderboard_result(old_leaderboard_result:Optional[dict[str, Any]], leaderboard_size, result_lists:tuple[list]):
    shop_week_list, shop_month_list, post_week_list, post_month_list, event_user_week_list, event_user_month_list = result_lists
    title = CONST_MAP.leaderboard_titles[2]
    content = 'Top %s Pass đồ xinh - Rinh xu shopping'
    data_map = {}
    for period in ['Tuần', 'Tháng']:
        event_user_list = event_user_week_list if period == 'Tuần' else event_user_month_list
        if old_leaderboard_result is None or len(old_leaderboard_result['data']) < 3:
            old_event_user_order = [None] * leaderboard_size
        else:
            old_event_user_order = old_leaderboard_result['data'][2][period]['ids']

        new_event_user_order = [item['user_id'] for item in event_user_list][:leaderboard_size]
        new_event_user_score = [item['point'] for item in event_user_list][:leaderboard_size]
        change_shop_rank = [(new_event_user_order.index(iid) - old_event_user_order.index(iid))
                            if iid in old_event_user_order else leaderboard_size
                            for iid in new_event_user_order][:leaderboard_size]

        data_map[period] = {
            'type':'user_account',
            'title':title,
            'content':content % len(new_event_user_order),
            'ids':new_event_user_order,
            'rank_change':change_shop_rank,
            'score':new_event_user_score
        }

    return title, data_map

from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Range

class LeaderboardDataItemSchema(Schema):
    type = fields.String(require=True, validate=[OneOf(['post', 'user_account'])])
    title = fields.String(require=True, validate=[OneOf(['Bài đăng', 'Shop', 'Pass đồ Rinh xu'])])
    content = fields.String(require=True)
    ids = fields.List(fields.Integer(strict=True, require=True, validate=[Range(min=1)]))
    rank_change = fields.List(fields.Integer(strict=True, require=True))
    score = fields.List(fields.Float(strict=True, required=True))
    user = fields.Raw()

class LeaderboardDataSchema(Schema):
    Tuần = fields.Nested(LeaderboardDataItemSchema)
    Tháng = fields.Nested(LeaderboardDataItemSchema)

class LeaderboardSchema(Schema):
    period = fields.List(fields.String(require=True), require=True)
    title = fields.List(fields.String(require=True), require=True)
    data = fields.List(fields.Nested(LeaderboardDataSchema))
