from src.utils.db_utils import execute_raw_query
from src.common.post_info_class import PostInfo
import datetime

def kol_post_source(filters) -> list[PostInfo]:
    # query = '''select p.id as pid, extract(epoch from p.created_at) as created_at, au.id as uid, au.avatar, au.full_name 
    # from post p join account_user au on p.user_id=au.id
    # where au.account_level_id =6
    # -- and p.is_public = true -- not unpublic
    # and p.is_deleted = false -- not deleted
    # '''
    query = '''
    select p.id as pid, p.created_at, au.id as uid, au.avatar, au.full_name 
    from post p join account_user au on p.user_id=au.id
    where au.account_level_id =6
    and p.is_deleted = false -- not deleted
    '''

    for filter_func in filters:
        query = filter_func(query)
    
    res = execute_raw_query(query)
    total_pi = []
    for pid, created_at, uid, avatar_url, full_name in res:
        pi = PostInfo(int(pid))
        pi.source_specific_info['uid'] = int(uid)
        pi.source_specific_info['timestamp'] = datetime.datetime.timestamp(created_at)#float(created_at)
        pi.source_specific_info['avatar_url'] = avatar_url
        pi.source_specific_info['full_name'] = full_name
        total_pi.append(pi)
    return total_pi


def order_by_recent_kol(query:str, male_item=False, interval_time='7 days') -> str:
    # query += '''
    # order by au.created_at > now() - interval '%s', p.created_at desc''' % str(interval_time)

    if male_item:
        sort_gender = 'p.gender_id asc'
    else:
        sort_gender = 'p.gender_id desc'
    query += '''
    order by %s, au.created_at > now() - interval '%s' desc, p.created_at desc
    ''' % (sort_gender, str(interval_time))

    return query


def check_recent_kol(interval_time='7 days'):
    query = '''select id
    from account_user au
    where au.account_level_id = 6
    and au.created_at > now() - interval :interval_time 
    order by created_at asc   
    '''
    res = execute_raw_query(query, interval_time=interval_time)
    recent_kol_ids = [int(i[0]) for i in res]

    return recent_kol_ids