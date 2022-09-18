from src.common.more_utils import order_selection
from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query

def get_hashtag_suggestion_raw(user_id:int) -> list[dict]:
    last_hashtags = get_last_hashtag_suggestion(user_id)
    keyword_hashtags = get_keyword_hashtag()
    stylish_hashtags = get_stylish_hashtag_suggestion()
    popular_hashtags = get_popular_hashtag_suggestion()
    existed_hashtag_ids = []

    last_hashtags = [item for item in last_hashtags if item['hashtag_id'] not in existed_hashtag_ids]
    existed_hashtag_ids += [item['hashtag_id'] for item in last_hashtags]

    keyword_hashtags = [item for item in keyword_hashtags if item['hashtag_id'] not in existed_hashtag_ids]
    existed_hashtag_ids += [item['hashtag_id'] for item in keyword_hashtags]

    stylish_hashtags = [item for item in stylish_hashtags if item['hashtag_id'] not in existed_hashtag_ids]
    existed_hashtag_ids += [item['hashtag_id'] for item in stylish_hashtags]

    popular_hashtags = [item for item in popular_hashtags if item['hashtag_id'] not in existed_hashtag_ids]
    existed_hashtag_ids += [item['hashtag_id'] for item in popular_hashtags]

    return last_hashtags, keyword_hashtags, stylish_hashtags, popular_hashtags

def get_hashtag_suggestion(user_id:int, number_of_hashtag:int) -> list[dict]:
    last_hashtags, keyword_hashtags, stylish_hashtags, popular_hashtags = get_hashtag_suggestion_raw(user_id)
    return (keyword_hashtags + last_hashtags + stylish_hashtags + popular_hashtags)[:number_of_hashtag]

def get_hashtag_suggestion_v2(user_id:int, number_of_hashtag:int) -> list[dict]:
    last_hashtags, keyword_hashtags, stylish_hashtags, popular_hashtags = get_hashtag_suggestion_raw(user_id)
    last_hashtags, keyword_hashtags, stylish_hashtags, popular_hashtags = order_selection([last_hashtags, keyword_hashtags, stylish_hashtags, popular_hashtags], [0.3, 0.2, 0.3, 0.2], number_of_hashtag)
    res = [
        {
            'text':'Hashtag gần đây',
            'hashtags':last_hashtags,
        },
        {
            'text':'Hashtag keyword',
            'hashtags':keyword_hashtags,
        },
        {
            'text':'Hashtag phong cách',
            'hashtags':stylish_hashtags,
        },
        {
            'text':'Hashtag phổ biến',
            'hashtags':popular_hashtags,
        }
    ]
    return res


def get_last_hashtag_suggestion(user_id:int) -> list[dict]:
    query = '''
    with recent_posts as (
        select id
        from post p
        where p.user_id = :user_id
        order by 1 desc
        limit 10
    ),
    recent_hashtags as (
        select h.id, regexp_replace(lower(regexp_replace(h.tag, '#.*', '', 'g')), '\W+', '', 'g') as name, h.total_posts 
        from recent_posts rp
        left join hashtag_post hp on hp.post_id = rp.id
        left join hashtag h on hp.hashtag_id = h.id
        order by h.id desc
    )
    select max(id) as hashtag_id, name, max(total_posts) as total_post
    from recent_hashtags
    where name not in (
            select lower(concat('Size', replace(s1."name", ' ', '')))
            from "size" s1
            --UNION
            --select lower(replace(s2."name", ' ', ''))
            --from "style" s2
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
    group by 2
    order by 1 desc
    limit 3
    '''
    raw_res = execute_raw_query(query, user_id=user_id)
    res = []
    for item in raw_res:
        res.append({
            "hashtag_id":int(item[0]),
            "total_post":int(item[2])
        })
    return res

def get_keyword_hashtag() -> list[dict]:
    query = '''
    select h.id, h.total_posts 
    from hashtag h 
    where id in :hashtag_ids
    '''
    raw_res = execute_raw_query(query, hashtag_ids=tuple(CONST_MAP.keyword_hashtag_ids))
    res = []
    for item in raw_res:
        res.append({
            "hashtag_id":int(item[0]),
            "total_post":int(item[1])
        })
    return res

def get_stylish_hashtag_suggestion() -> list[dict]:
    query = '''
    with prun_hashtag as (
        select h.id, regexp_replace(lower(regexp_replace(h.tag, '#.*', '', 'g')), '\W+', '', 'g') as name, h.total_posts 
        from hashtag h
        where h.total_posts > 0
    ),
    selected_hashtag as (
        select *
        from prun_hashtag h
        where h.name in (
            select lower(replace(s."name", ' ', ''))
            from "style" s
        )
    )
    select sh.name, min(id) as id, sum(total_posts) as total_posts, random()
    from selected_hashtag sh 
    where id in (77,6357,4647,1097,240,93,55,6641,81,6194,3550,399,3928,2683,5840,391,4377,228,2709,266,73,6692,1940,381,270,8048)
    group by 1
    order by 4 desc
    limit 6
    '''
    raw_res = execute_raw_query(query)
    res = []
    for item in raw_res:
        res.append({
            "hashtag_id":int(item[1]),
            "total_post":int(item[2])
        })
    return res

def get_popular_hashtag_suggestion() -> list[dict]:
    query = '''
    with recent_hashtag as (
        select hp.hashtag_id, count(distinct p.user_id) as total_users
        from post p join hashtag_post hp on p.id = hp.post_id 
        where p.created_at >= current_date - interval ':day days'
        and hp.hashtag_id not in (1,3,4,5,53,56,58,60,71,74,78,195,197,236,237)
        group by hashtag_id 
        order by total_users desc 
        limit :limit
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
        select name, min(hashtag_id::text) as list_hashtag_ids, sum(sh.total_users) as total_users, sum(sh.total_posts) as total_posts
        from selected_hashtag sh
        group by 1
        order by 3 desc
    )
    select list_hashtag_ids, total_posts
    from top_post_hashtag
    '''
    raw_res = execute_raw_query(query, day=CONST_MAP.time_limit_medium, limit=CONST_MAP.post_limit_medium)
    res = []
    for item in raw_res:
        res.append({
            "hashtag_id":int(item[0]),
            "total_post":int(item[1])
        })
    return res