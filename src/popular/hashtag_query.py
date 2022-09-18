import random

from numpy import append
from src.common.score_decay import post_score_modify
from src.common.current_time import get_query_time_str
from src.utils.db_utils import execute_raw_query
from src.utils.try_convert import try_float
from src.popular.hashtag_normalize import normalize_tag, id_str_to_id_list
from src.utils.redis_caching import redis_result_cache
from src.const import const_map as CONST_MAP
import logging
deviation_logger = logging.getLogger('deviation_logger')

# @redis_result_cache(lambda x: ['hashtag:v3:post:%s' % x], expire_secs=3600)
def query_phobien() -> tuple[list[str], list[list[int]], list[int]]:
    number_of_hashtag = 100
    query = '''
    with recent_hashtag as (
        select hp.hashtag_id, count(distinct p.user_id) as total_users
        from post p join hashtag_post hp on p.id = hp.post_id 
        where p.created_at >= current_date - interval '%s days'
        and hp.hashtag_id not in (1,3,4,5,53,56,58,60,71,74,78,195,197,236,237)
        group by hashtag_id 
        order by total_users desc 
    ),
    prun_hashtag as (
        select rh.*, regexp_replace(lower(regexp_replace(h.tag, '#.*', '', 'g')), '\W+', '', 'g') as name, h.total_posts
        from recent_hashtag rh left join hashtag h on rh.hashtag_id = h.id
    ),
    selected_hashtag as (
        select *
        from prun_hashtag h
        where h.name not in (
            select lower(concat('Size', replace(s1."name", ' ', '')))
            from "size" s1
            UNION
            select lower(replace(s2."name", ' ', ''))
            from "style" s2
            UNION
            select lower(replace(c1."name", ' ', ''))
            from category c1
            UNION
            select lower(replace(c2."name", ' ', ''))
            from "condition" c2
            UNION
            select lower(replace(p1."name", ' ', ''))
            from "period" p1
            UNION
            select lower(concat('new', replace(c2."name", ' ', '')))
            from "condition" c2
            UNION
            select lower(replace(c3."tag", ' ', ''))
            from country_area c3
            where tag is not null
            union 
            select '99'
            union
            select 'nobrand'
        )
        and length(h.name) < 20
        order by h.total_posts desc
    ),
    top_post_hashtag as (
        select name, string_agg(hashtag_id::text, ', ') as list_hashtag_ids, sum(sh.total_users) as total_users, sum(sh.total_posts) as total_posts
        from selected_hashtag sh
        group by 1
        order by 3 desc
    )
    select *
    from top_post_hashtag
    where length(name) < 30
    and name != ''
    limit :limit
    ''' % CONST_MAP.time_limit_long
    raw_res = execute_raw_query(query, limit=number_of_hashtag)
    res = [(str(tag), id_str_to_id_list(idstr), int(total_posts)) for tag, idstr, total_users, total_posts in raw_res if len(str(tag)) > 0]
    if len(res) < 1:
        return [], [], []
    tags, post_ids, total_posts = zip(*res)
    return list(tags), list(post_ids), list(total_posts)

def query_thinhhanh() -> tuple[list[str], list[list[int]], list[int]]:
    number_of_hashtag = 100
    query = '''
    with recent_hashtag as (
        select hp.hashtag_id, count(distinct p.user_id) as total_posts
        from post p join hashtag_post hp on p.id=hp.post_id 
        where p.created_at >= current_date - interval '%s days'
        and hp.hashtag_id not in (1,3,4,5,53,56,58,60,71,74,78,195,197,236,237)
        group by hashtag_id 
        order by total_posts desc 
    ),
    prun_hashtag as (
        select rh.*, regexp_replace(lower(regexp_replace(h.tag, '#.*', '', 'g')), '\W+', '', 'g') as name
        from recent_hashtag rh left join hashtag h on rh.hashtag_id = h.id
    ),
    selected_hashtag as (
        select *
        from prun_hashtag h
        where h.name not in (
            select lower(concat('Size', replace(s1."name", ' ', '')))
            from "size" s1
            UNION
            select lower(replace(c1."name", ' ', ''))
            from category c1
            UNION
            select lower(replace(c2."name", ' ', ''))
            from "condition" c2
            UNION
            select lower(replace(p1."name", ' ', ''))
            from "period" p1
            UNION
            select lower(replace(c3."tag", ' ', ''))
            from country_area c3
            where tag is not null
            union 
            select '99'
            union
            select 'nobrand'
        )
        order by h.total_posts desc
    ),
    top_post_hashtag as (
        select name, string_agg(hashtag_id::text, ', ') as list_hashtag_ids, sum(sh.total_posts)
        from selected_hashtag sh
        group by 1
        order by 3 desc
    )
    select *
    from top_post_hashtag
    where length(name) < 30
    and name != ''
    limit :limit
    ''' % CONST_MAP.time_limit_long
    raw_res = execute_raw_query(query, limit=number_of_hashtag)
    res = [(str(tag), id_str_to_id_list(idstr), int(total_posts)) for tag, idstr, total_posts in raw_res if len(str(tag)) > 0]
    if len(res) < 1:
        return [], [], []
    tags, post_ids, total_posts = zip(*res)
    return list(tags), list(post_ids), list(total_posts)

# @redis_result_cache(lambda x: ['hashtag:v3:like:%s' % x], expire_secs=3600)
def query_yeuthich() -> tuple[list[str], list[list[int]], list[int]]:
    number_of_hashtag = 100
    query = '''
    with recent_hashtag as (
        select hp.hashtag_id, sum(p.total_favorites) as total_favorites_count
        from post p join hashtag_post hp on p.id=hp.post_id 
        where p.created_at >= current_date - interval '%s days'
        and hp.hashtag_id not in (1,3,4,5,53,56,58,60,71,74,78,195,197,236,237)
        group by hashtag_id 
        order by total_favorites_count desc 
    ),
    prun_hashtag as (
        select rh.*, regexp_replace(lower(regexp_replace(h.tag, '#.*', '', 'g')), '\W+', '', 'g') as name, h.total_posts 
        from recent_hashtag rh left join hashtag h on rh.hashtag_id = h.id
    ),
    selected_hashtag as (
        select *
        from prun_hashtag h
        where h.name not in (
            select lower(concat('Size', replace(s1."name", ' ', '')))
            from "size" s1
            UNION
            select lower(replace(c1."name", ' ', ''))
            from category c1
            UNION
            select lower(replace(c2."name", ' ', ''))
            from "condition" c2
            UNION
            select lower(replace(p1."name", ' ', ''))
            from "period" p1
            UNION
            select lower(replace(c3."tag", ' ', ''))
            from country_area c3
            where tag is not null
            union 
            select '99'
            union
            select 'nobrand'
        )
        order by h.total_favorites_count desc
    ),
    top_like_hashtag as (
        select name, string_agg(hashtag_id::text, ', ') as list_hashtag_ids, sum(sh.total_favorites_count) as total_likes, sum(sh.total_posts) as total_post
        from selected_hashtag sh
        group by 1
        order by 3 desc
    )
    select *
    from top_like_hashtag
    where length(name) < 30
    and name != ''
    limit :limit
    ''' % CONST_MAP.time_limit_long
    raw_res = execute_raw_query(query, limit=number_of_hashtag)
    res = [(str(tag), id_str_to_id_list(idstr), int(total_posts)) for tag, idstr, total_likes, total_posts in raw_res if len(str(tag)) > 0]
    if len(res) < 1:
        return [], [], []
    tags, post_ids, total_posts = zip(*res)
    return list(tags), list(post_ids), list(total_posts)

def query_curating_posts(curating_users:list[int]) -> tuple[int, list[int]]:
    if len(curating_users) < 1:
        return 0, []
    query = '''
    select p.id from post p
    where p.user_id in (
        select id
        from account_user au
        where au.account_level_id in (
            select id
            from account_level al
            where al.slug like 'curator%%'
        )
    )
    and p.created_at >= now() - interval '%s days'
    and p.is_deleted = false
    and p.is_sold = false
    order by created_at desc
    limit 50''' % CONST_MAP.time_limit_long
    raw_res = execute_raw_query(query, users=tuple(curating_users))
    post_ids = [int(item[0]) for item in raw_res]
    return len(post_ids), post_ids

def query_keywork_by_search_count(timeframe:int) -> list[str]:
    query = '''
    select lower(sl.keyword), count(*)
    from searching_log sl
    where sl.created_at >  %s - interval '1 days'
    and lower(sl.keyword) not in (
            select lower(c."name")
            from category c
    )
    and lower(sl.keyword) not in (
            '', '2hand', 'áo', 'giày', 'đầm', 'set quần áo', 'áo khoác ngoài', 'quần','chân váy','túi', 'phụ kiện', 'đồ thể thao', 'đồ len', '99%%'
    )
    group by "keyword"
    order by "count" desc, "keyword" asc
    limit 20''' % get_query_time_str()
    raw_res = execute_raw_query(query, days=timeframe)
    return [item[0] for item in raw_res]

def query_hashtag_post(hashtag_id_list_of_list:list[list[int]]) -> tuple[list[list[int]], list[list[float]]]:
    query = '''
    with sample as (
        select distinct hp.post_id, p.total_favorites, p.created_at::date, 
            p.ai_metadata -> 'post_score' -> 'total' as score, 
            p.user_id,
            p.created_at as created_at1,
            (p.ai_metadata->'user_ordinal')::int as user_ordinal
        from hashtag_post hp left join top_posts p on hp.post_id = p.id
        where hp.hashtag_id in :hashtag_ids 
        and p.is_sold = false
        and p.is_deleted = false 
        and p.is_public = true
        order by p.created_at::date desc, p.total_favorites desc
        limit 999
    )
    select s.post_id, 
    s.score, 
    extract(day from now() - s.created_at1) as post_age, 
    extract(day from now() - au.last_online) as last_online, 
    s.user_ordinal
    from sample s join top_sellers au on s.user_id = au.id
    '''
    hashtag_post_ids: list[list[int]] = []
    hashtag_post_scores: list[list[float]] = []
    for hashtag_ids in hashtag_id_list_of_list:
        res = execute_raw_query(query, hashtag_ids=tuple(hashtag_ids))
        post_ids: list[int] = []
        scores: list[float] = []
        for pid, score, post_age, last_online, user_ordinal in res:
            post_ids.append(pid)
            if score is None:
                score = 0
            scores.append(post_score_modify(try_float(score, 0), post_age, last_online, user_ordinal))
        hashtag_post_ids.append(post_ids)
        hashtag_post_scores.append(scores)
    return hashtag_post_ids, hashtag_post_scores