from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query


def solr_top_posts_filter(post_ids: list):
    query = '''
    select id
    from post p 
    where 1=1
    and p.id in :post_ids
    and p.id in (select id from eligible_posts)
    order by 
        p.id in (select id from top_posts) desc,
        array_position(ARRAY[%s]::int[], p.id)
    ''' % ','.join(['%s' % id for id in post_ids])

    res = execute_raw_query(query, post_ids=tuple(post_ids))
    post_ids = [int(i[0]) for i in res]
    return post_ids



def solr_top_sellers_filter():
    pass