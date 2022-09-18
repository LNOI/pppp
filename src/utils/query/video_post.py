from src.common.current_time import get_query_time_str
from src.utils.db_utils import execute_raw_query

from typing import Tuple, List, Dict

def query_video_post(hour_limit, number_of_post, avoid_user_id, keep_sold=False):
    if len(avoid_user_id) > 0:
        avoid_user_condition = 'and p.user_id not in (%s)' % ','.join([str(i) for i in avoid_user_id])
    else:
        avoid_user_condition = ''
    if keep_sold==False:
        query = '''
        select p.id from post p join media m2 on p.id = m2.post_id 
        where m2.mime_type ='video' 
        and p.created_at > %s - interval ':hour_limit hours'
        and p.is_deleted = false
        and p.is_for_sale = true
        and p.is_sold = false %s
        limit :limit
        ''' % (get_query_time_str(), avoid_user_condition)
    else:
        query = '''
        select p.id from post p join media m2 on p.id = m2.post_id 
        where m2.mime_type ='video' 
        and p.created_at > %s - interval ':hour_limit hours'
        and p.is_deleted = false %s
        limit :limit
        ''' % (get_query_time_str(), avoid_user_condition)
    res = execute_raw_query(query, hour_limit=hour_limit, limit=number_of_post)
    return [int(i[0]) for i in res]
