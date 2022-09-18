from src.utils.db_utils import execute_raw_query
from src.common.post_info_class import PostInfo
from src.const import const_map as CONST_MAP

def popular_post_source(filters):
    query = '''
    with top_id as (
        select p.id, count(*)::float/sqrt(avg(p.total_views)) as score 
        from wishlist w 
        left join eligible_posts p on p.id = w.post_id 
        where w.created_at > now() - interval '1 week'
        and p.is_public = true -- not unpublic
        and p.is_deleted = false -- not deleted
        and p.is_for_sale = true
        and p.total_views >= :view_limit
        and p.total_favorites >= :like_limit
        group by p.id
    ),
    top_table as (
        select p.*, ti.score as popular_score
        from eligible_posts p join top_id ti
        on p.id=ti.id
    ),
    rank_table as (
        select row_number() over (partition by tp.category_id order by tp.score desc) as row, tp.*
        from top_table tp
    )
    select id, p.popular_score as score
    from rank_table p
    where true
    '''

    for filter_func in filters:
        query = filter_func(query)
    query_result = execute_raw_query(query, view_limit=CONST_MAP.popular_post_view_limit, like_limit=CONST_MAP.popular_post_like_limit)
    popular_post_infos = []
    for item in query_result:
        if item[0] is None or item[1] is None:
            continue
        post_info = PostInfo(int(item[0]))
        post_info.source_specific_info['popular_score'] = float(item[1])
        popular_post_infos.append(post_info)
    return popular_post_infos