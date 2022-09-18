import random
import logging

from asyncio.log import logger
from marshmallow import Schema, fields

from src.utils.try_convert import try_int
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_s3_presign_url
from src.const.global_map import RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.const.global_map import CONFIG_SET
from src.carousel.watchnext_post import get_simple_filtered_post_info
from src.advertising.ads_util import get_ads_acc, get_post_from_ads_acc
from src.common.source.active_user_source import eligible_users_filter
from src.common.solr_search_filter import solr_top_posts_filter, solr_top_sellers_filter

deviation_logger = logging.getLogger('deviation_logger')


def search_keyword(user_id: int, keyword: str, filter_args: dict, limit=CONST_MAP.post_limit_small):
    keyword_res = RESOURCE_MAP['solr_search_client'].search(
        keyword, **{'rows': limit * 3, 'fq': 'type:post', 'fl': 'id', 'q.op': 'OR', 'defType': 'edismax'})
    # pids = [int(kr['id'].split('_')[-1]) for kr in keyword_res]

    pids = [int(kr['id'].split('_')[-1]) for kr in keyword_res]
    if len(pids) > 0:
        # eligible_pids = get_simple_filtered_post_info(pids, filter_args, limit)[:limit]
        # eligible_pids = [pi.pid for pi in eligible_pids]
        # selected_pids = [pid for pid in pids if pid in eligible_pids]

        selected_pids = solr_top_posts_filter(post_ids=pids)
        
    else:
        selected_pids = []

    # Add ads post to Search result
    try:
        ads_post = get_post_from_ads_acc(no_post=CONST_MAP.ads_search_slot, ads_type='search', pids=selected_pids)
        if ads_post:
            # add ads post to from index 1 and dex 3
            if len(ads_post) == 1:
                selected_pids[1:1] = ads_post[0:1]
            else:
                selected_pids[1:1] = ads_post[:int(len(ads_post)/2)]
                selected_pids[3:3] = ads_post[:int(len(ads_post))]
            # de-duplicate selected post
            selected_pids = list(dict.fromkeys(selected_pids))
        else:
            pass

    except Exception as e:
        deviation_logger.info(f"Failed to load Ads post: {e}")



    account_res = RESOURCE_MAP['solr_search_client'].search(
        keyword, **{'rows': limit, 'fq': 'type:account', 'q.op': 'OR', 'defType': 'edismax'})
    uids = [int(ar['id'].split('_')[-1]) for ar in account_res]

    # Remove block acc
    filtered_uids = eligible_users_filter(uids=uids)
    uids = [y for x in uids for y in filtered_uids if y == x]
    # Add ads account to Search result
    try:
        # uids.append(266003)
        # if CONST_MAP.test_mode == True and user_id in CONST_MAP.home_api_test_user:
        ads_acc = get_ads_acc(no_acc=CONST_MAP.ads_search_slot, ads_type='search', uids=uids)
        if ads_acc:
            if len(ads_acc) == 1:
                uids[1:1] = ads_acc[0:1]
            else:
                uids[1:1] = ads_acc[:int(len(ads_acc)/2)]
                uids[3:3] = ads_acc[:int(len(ads_acc))]
            uids = list(dict.fromkeys(uids))
        else:
            deviation_logger.info(f"There is no account running Advertisement.")
    except Exception as e:
        deviation_logger.info(f"Failed to load Ads account: {e}")

    keyword_without_space = ''.join(keyword.split())
    hashtag_res = RESOURCE_MAP['solr_search_client'].search(
        keyword_without_space, **{'rows': limit, 'fq': 'type:hashtag', 'fl': 'id, field_ids, text_f_name', 'q.op': 'OR', 'defType': 'edismax'})
    hashtag_items = []
    for item in hashtag_res:
        try:
            hashtag_items.append(
                {
                    'id': int(item['id'].split('_')[-1]),
                    'all_related_ids': [int(i) for i in item['field_ids'].split(',')],
                    'name': str(item['text_f_name'][0])
                })
        except Exception as e:
            deviation_logger.info(
                'Search: hashtag: error %s: %s' % (e, str(item)))

    add_hashtag_info(hashtag_items)
    hashtag_map_result = [
        {
            'name': item['name'],
            'post_ids':item['post_ids'],
            'total_post':item['total_post'],
            'total_view':item['total_view']
        }
        for item in hashtag_items[:limit]
    ]
    return {
        'hashtag': hashtag_map_result,
        'post': selected_pids[:limit],
        'account': uids[:limit]
    }


def add_hashtag_info(hashtag_objs):
    if len(hashtag_objs) < 1:
        return hashtag_objs
    main_hashtag_ids = [item['id'] for item in hashtag_objs]
    # get hashtag count info
    count_query = '''
    select id, total_posts, total_views 
    from hashtag h 
    where h.id in :hashtag_ids 
    '''
    res = execute_raw_query(count_query, hashtag_ids=tuple(main_hashtag_ids))
    count_info_map = {
        int(item[0]): [try_int(item[1], 0), try_int(item[2], 0)]
        for item in res
    }
    # get hashtag post info
    post_query = '''
    with hashtag_data as (
        select row_number() over (partition by hp.hashtag_id order by hp.post_id desc), hp.hashtag_id, hp.post_id
        from hashtag_post hp
        where hp.hashtag_id in :hashtag_ids 
        order by id desc
        limit 9999
    )
    select hashtag_id, string_agg(post_id::text, ',')
    from hashtag_data
    where row_number < :limit
    group by hashtag_id
    '''
    post_res = execute_raw_query(post_query, hashtag_ids=tuple(
        main_hashtag_ids), limit=CONST_MAP.post_limit_small)
    hashtag_post_info_map = {
        int(item[0]): [int(pid) for pid in item[1].split(',')]
        for item in post_res
    }
    # add info to object
    for item in hashtag_objs:
        if item['id'] in hashtag_post_info_map:
            item['post_ids'] = hashtag_post_info_map[item['id']]
            item['total_post'] = len(item['post_ids'])
        else:
            item['post_ids'] = []
            item['total_post'] = 0
        if item['id'] in count_info_map:
            item['total_view'] = count_info_map[item['id']][1]
        else:
            item['total_view'] = 0


def get_thumbnails_solr(keyword: list[str], filter_args: dict, limit=CONST_MAP.post_limit_small):
    keyword_res = RESOURCE_MAP['solr_search_client'].search(
        keyword, **{'rows': limit * 3, 'fq': 'type:post', 'q.op': 'OR', 'defType': 'edismax'})
    pids = [int(kr['id'].split('_')[-1]) for kr in keyword_res]
    if len(pids) > 0:
        eligible_pis = get_simple_filtered_post_info(pids, filter_args, limit)
        eligible_pids = [pi.pid for pi in eligible_pis]
        selected_pids = [pid for pid in pids if pid in eligible_pids]
        remain_pids = [pid for pid in pids if pid not in selected_pids]
        remain_pids_top = remain_pids[:10]
        remain_pids_mid = remain_pids[10:50]
        remain_pids_bottom = remain_pids[50:]
        random.shuffle(remain_pids_top)
        random.shuffle(remain_pids_mid)
        random.shuffle(remain_pids_bottom)
        if len(selected_pids) < limit:
            selected_pids = selected_pids + remain_pids_top + remain_pids_mid + remain_pids_bottom
    else:
        selected_pids = []
    
    selected_thumbnails = []
    for pid in selected_pids:
        try:
            query = '''
            select p.thumbnail 
            from post p 
            where p.id=:pid
            '''
            res = execute_raw_query(query, pid=pid)
            if len(res) > 0:
                s3_url = res[0][0]
                s3_presign_url = minio_s3_presign_url(s3_url)
                selected_thumbnails.append(s3_presign_url)
        except Exception as e:
            if CONFIG_SET == 'prod':
                deviation_logger.info(
                    'Get img for postid %s failed: %s' % (pid, e), exc_info=True)
    # return res_kw, res_img
    return selected_pids, selected_thumbnails


