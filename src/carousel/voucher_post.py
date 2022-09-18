from src.common.more_utils import split_post_infos_by_user
from src.common.post_info_class import add_post_score_info, PostInfo
from src.utils.db_utils import execute_raw_query
from src.common.random_shuffle import random_post_info_shuffle
from src.carousel.common import get_user_thubmnail_post_id
from src.const import const_map as CONST_MAP

# @redis_cache_json(lambda :'promotion_post', expire_secs=3600*6)
def get_voucher_post_info():
    summary_data_query = '''
    select min_spent_amount, account_level_id, seller_ids 
    from discount_voucher dv 
    where now() > dv.start_date 
    and now() < dv.end_date 
    and dv.used < dv.usage_limit 
    and (dv.account_level_id is not null or dv.seller_ids != '{}')
    '''
    res = execute_raw_query(summary_data_query)
    summary_data_filter = []
    for row in res:
        single_data_filter = {
            'user_id':'true',
            'amount':'true',
            'account_level_id':'true'
        }
        if row[0] is not None:
            single_data_filter['amount'] = ' (p.amount >= %d) ' % float(row[0])
        if row[1] is not None:
            single_data_filter['account_level_id'] = ' (au.account_level_id = %d) ' % int(row[1])
        if row[2] is not None and len(row[2]) > 0:
            single_data_filter['user_id'] = ' (p.user_id in (%s)) ' % ','.join([str(i) for i in row[2]])
        summary_data_filter.append(single_data_filter)
    
    voucher_query = '''
    select p.id, p.user_id, (p.ai_metadata->'post_score'->'media')::float as score
    from top_posts p
    left join account_user au on au.id = p.user_id
    where p.is_for_sale = true
    and p.is_sold = false
    '''
    if len(summary_data_filter) > 0:
        voucher_condition_sql = []
        for single_filter_map in summary_data_filter:
            voucher_condition_sql.append('(%s)' % (' and '.join([single_filter_map['amount'], single_filter_map['account_level_id'], single_filter_map['user_id']])))
        voucher_query += 'and (%s)' % ' or '.join(voucher_condition_sql)
    
    res = execute_raw_query(voucher_query, offline_day_limit=CONST_MAP.offline_time_limit, day_limit=CONST_MAP.time_limit_long, post_limit=CONST_MAP.post_limit_medium)
    post_infos = []
    for item in res:
        post_info = PostInfo(int(item[0]))
        post_info.source_specific_info['user_id'] = int(item[1])
        post_infos.append(post_info)
    return post_infos

def get_voucher_in_shop_format():
    post_infos = get_voucher_post_info()
    shop_pi_map = split_post_infos_by_user(post_infos)
    res = [
        {
            'shop_id': shop_id,
            'shop_post_ids': [pi.pid for pi in shop_pi_map[shop_id]],
            'thumbnail_post_ids': get_user_thubmnail_post_id(shop_id)
        }
        for shop_id in shop_pi_map
    ]
    return res

def get_processed_voucher_post_infos():
    post_infos = get_voucher_post_info()
    add_post_score_info(post_infos)
    post_infos = random_post_info_shuffle(post_infos)
    return post_infos
