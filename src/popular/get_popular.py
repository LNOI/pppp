import time
import json
import random
from marshmallow import Schema, fields
from collections import OrderedDict
from typing import Any, List, Dict, Union

from src.common.more_utils import order_selection
from src.common.random_shuffle import random_shuffle
from src.const import const_map as CONST_MAP
from src.const.global_map import CONFIG_SET
from src.popular.hashtag_query import query_thinhhanh, query_phobien, query_yeuthich, query_curating_posts, query_keywork_by_search_count, query_hashtag_post
from src.popular.solr_search import get_thumbnails_solr
from src.recommendation.source.shop_source import shop_queue_for_hashtag
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_s3_presign_url, minio_download_to_bytes
from src.utils.redis_caching import redis_cache_json
from src.carousel.cheap_2hand import get_cheap_2hand_post
from src.carousel.luxury_2hand import get_luxury_2hand_post
from src.carousel.recent_2hand import get_recent_2hand_post
from src.carousel.sss_tip import get_sss_tip_post



import logging
deviation_logger = logging.getLogger('deviation_logger')


@redis_cache_json(lambda x: 'hashtag:v4:cachable:%s' % x, expire_secs=3600*6)
def get_cachable_hashtag(number_of_hashtag: int):
    tags, hashtag_ids, total_posts = query_thinhhanh()
    post_id_lists, post_scores = query_hashtag_post(hashtag_ids)
    thinhhanh_hashtag: list[dict[str, Union[str, int, list[int], list[float]]]] = [
        {
            'hashtag': '#'+tag,
            'total_post': count,
            'post_id': ids,
            'post_scores': scores,
            'subtitle': 'thịnh hành'
        }
        for tag, count, ids, scores in zip(tags, total_posts, post_id_lists, post_scores) if len(ids) > 0
    ]

    tags, hashtag_ids, total_posts = query_yeuthich()
    post_id_lists, post_scores = query_hashtag_post(hashtag_ids)
    yeuthich_hashtag: list[dict[str, Union[str, int, list[int], list[float]]]] = [
        {
            'hashtag': '#'+tag,
            'total_post': count,
            'post_id': ids,
            'post_scores': scores,
            'subtitle': 'yêu thích'
        }
        for tag, count, ids, scores in zip(tags, total_posts, post_id_lists, post_scores) if len(ids) > 0
    ]

    total_hashtags = thinhhanh_hashtag + yeuthich_hashtag
    sorted_hashtag = sorted(
        total_hashtags, key=lambda x: x['total_post'], reverse=True)
    selected_hashtag = []
    cropped_result: list[dict[str,
                              Union[str, int, list[int], list[float]]]] = []
    for item in sorted_hashtag:
        if item['hashtag'] not in selected_hashtag:
            selected_hashtag.append(item['hashtag'])
            cropped_result.append(item)
        if len(cropped_result) >= number_of_hashtag:
            break

    total_post, post_ids = query_curating_posts(CONST_MAP.feature_user_id)
    curating_hashtag = [{'hashtag': '#CảmHứngThờiTrang', 'total_post': total_post,
                         'post_id': post_ids, 'subtitle': 'Editor’s choice'}]
    tip_posts = get_sss_tip_post()
    tip_hashtag = [{'hashtag': '#SSSTips', 'total_post': len(
        tip_posts), 'post_id': tip_posts, 'subtitle': 'Tất tần tật về SSS'}]

    luxury_post_ids = get_luxury_2hand_post()['post_ids'][:999]
    luxury_hashtag = [{'hashtag': '#HàngHiệu', 'total_post': len(
        luxury_post_ids), 'post_id': luxury_post_ids, 'subtitle': 'Secondhand hàng hiệu'}]

    recent_post_ids = get_recent_2hand_post()['post_ids'][:999]
    recent_hashtag = [{'hashtag': '#2handMớiVề', 'total_post': len(
        recent_post_ids), 'post_id': recent_post_ids, 'subtitle': 'Mại dzô mại dzô'}]

    cheap_post_ids = get_cheap_2hand_post()['post_ids'][:999]
    cheap_hashtag = [{'hashtag': '#CựcRẻ', 'total_post': len(
        cheap_post_ids), 'post_id': cheap_post_ids, 'subtitle': 'Thử là nghiện'}]
    before_result = curating_hashtag + tip_hashtag
    after_result = luxury_hashtag + recent_hashtag + cheap_hashtag + cropped_result
    final_result = [before_result, after_result]
    return final_result


def get_uncache_hashtag():
    shop_map = shop_queue_for_hashtag()
    shop_ids = list(shop_map.keys())
    if len(shop_ids) > 0:
        random.shuffle(shop_ids)
        selected_shop_id = shop_ids[0]
        sss_id_query = '''
        select au.sss_id 
        from eligible_users au 
        where au.id = :shop_id
        '''
        res = execute_raw_query(sss_id_query, shop_id=selected_shop_id)
        sss_id = str(res[0][0])
        shop_hashtag = [{'hashtag': '#%s' % sss_id, 'total_post': len(
            shop_map[selected_shop_id]), 'post_id':shop_map[selected_shop_id], 'subtitle':'được tài trợ'}]
        return shop_hashtag
    else:
        return []


def get_popular_hashtag_v2(number_of_hashtag: int) -> list[dict[str, Union[str, int, list[int]]]]:
    before_result, after_result = get_cachable_hashtag(number_of_hashtag)
    uncache_result = get_uncache_hashtag()
    final = before_result + uncache_result + after_result
    s = time.time()
    for item in final:
        if 'post_scores' in item:
            item['post_id'] = random_shuffle(
                item['post_id'], item['post_scores'])
            del item['post_scores']
    e = time.time()
    print('shuffle time: %s' % (e-s))
    return final[:number_of_hashtag]


@redis_cache_json(lambda x: 'keyword:v2:final:%s' % x, expire_secs=3600)
def get_popular_keyword_v2(number_of_keyword: int) -> List[Dict[str, str]]:
    timeframe = CONST_MAP.hashtag_timeframe_day_limit

    search_keywork = query_keywork_by_search_count(timeframe)

    total_keywords = CONST_MAP.keyword_list.copy()
    normalized_keywords = [kw.lower() for kw in total_keywords]
    for kw in search_keywork:
        if kw.lower() not in normalized_keywords:
            total_keywords.append(kw)
            normalized_keywords.append(kw.lower())
    keywords = list(OrderedDict.fromkeys(total_keywords))
    keywords, keyword_imgs_url = get_keyword_img(keywords)
    result = []
    for kw, img_url in zip(keywords[:number_of_keyword], keyword_imgs_url[:number_of_keyword]):
        result.append({
            'keyword': kw,
            'image_url': img_url
        })
    return result


def get_keyword_img(keywords: list[str]) -> tuple[list[str], list[str]]:
    res_kw = []
    res_img = []
    for kw in keywords:
        try:
            query = '''
            select p.thumbnail 
            from post p join account_user au on p.user_id = au.id 
            where LOWER(p.caption) like :keyword or LOWER(p.item_name) like :keyword 
            or LOWER(au.sss_id) like :keyword 
            limit 1
            '''
            res = execute_raw_query(query, keyword=f'%{kw}%')
            if len(res) > 0:
                s3_url = res[0][0]
                s3_presign_url = minio_s3_presign_url(s3_url)
                res_kw.append(kw)
                res_img.append(s3_presign_url)
        except Exception as e:
            if CONFIG_SET == 'prod':
                deviation_logger.info(
                    'Get img for keyword %s failed: %s' % (kw, e), exc_info=True)
    return res_kw, res_img


def get_keyword_suggestion(user_id:int, number_of_suggestion:int) -> dict[str,list[str]]:
    recent_query = '''
    select au.metadata->'recent_searches' as recent_search
    from account_user au 
    where au.id = :user_id
    '''
    recent_res = execute_raw_query(recent_query, user_id=user_id)
    if recent_res == [] or recent_res[0][0] is None:
        recent_keywords = []
    else:
        recent_keywords = [str(i) for i in recent_res[0][0]]
    
    popular_keyword_query = '''
    with kw as (
        select LTRIM(RTRIM(sl.keyword)) as keyword, sqrt(count(*)) as score
        from searching_log sl 
        where sl.created_at > now() - interval '1 week'
        and sl.keyword != ''
        group by keyword
        order by score desc
    )
    select kw.keyword, kw.score
    from kw
    where score > 3
    '''
    keyword_res = execute_raw_query(popular_keyword_query)
    keywords = []
    keyword_scores = []
    for item in keyword_res:
        if str(item[0]) not in recent_keywords:
            keywords.append(str(item[0]))
            keyword_scores.append(int(item[1]))
    selected_keywords = random_shuffle(keywords, keyword_scores)

    sss_suggestion = [i for i in CONST_MAP.keyword_sss_suggestion if i not in recent_keywords+selected_keywords]
    random.shuffle(sss_suggestion)
    recent_keywords, selected_keywords, sss_suggestion = order_selection([recent_keywords, selected_keywords, sss_suggestion],
     [0.1, 0.3, 0.6], number_of_suggestion)
    return [
        {
            'text':'Tìm kiếm gần đây',
            'keywords':recent_keywords
        },
        {
            'text':' Top tìm kiếm',
            'keywords':selected_keywords
        },
        {
            'text':'SSSMarket gợi ý',
            'keywords':sss_suggestion
        }
    ]

# TODO: Cache keyword_suggestion
def get_keyword_suggestion_v2(user_id: int, number_of_suggestion: int) -> dict[str, list[str]]:
    recent_query = '''
    select au.metadata->'recent_searches' as recent_search
    from account_user au 
    where au.id = :user_id
    '''
    # Query recent search
    recent_res = execute_raw_query(recent_query, user_id=user_id)
    if recent_res == [] or recent_res[0][0] is None:
        recent_keywords = []
    else:
        recent_keywords = [str(i) for i in recent_res[0][0]]

    popular_keyword_query = '''
    with kw as (
        select LTRIM(RTRIM(sl.keyword)) as keyword, sqrt(count(*)) as score
        from searching_log sl 
        where sl.created_at > now() - interval '1 week'
        and sl.keyword != ''
        group by keyword
        order by score desc
    )
    select kw.keyword, kw.score
    from kw
    where score > 3
    '''
    # Query popular keywords
    keyword_res = execute_raw_query(popular_keyword_query)
    keywords = []
    keyword_scores = []
    for item in keyword_res:
        if str(item[0]) not in recent_keywords:
            keywords.append(str(item[0]))
            keyword_scores.append(int(item[1]))
    # Popular keywords
    selected_keywords = random_shuffle(keywords, keyword_scores)
    selected_keywords = [i for i in selected_keywords if i not in CONST_MAP.keyword_sss_suggestion]

    # Prepare pre-filter
    filter_args = {
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }

    # SSS suggestion based on config keywords
    sss_suggestion = [i for i in CONST_MAP.keyword_sss_suggestion if i not in recent_keywords]
    sss_suggestion_pno = {
        'keyword': str,
        'post_number': int
    }
    filter_sss_suggestion = []
    for kw in sss_suggestion:
        if kw in ('boots', 'jeans'):
            query = '''
            select count(*) 
            from eligible_posts p
            where LOWER(p.caption) like :keyword
            or LOWER(p.item_name) like :keyword
            and p.is_deleted = false and p.is_sold = False
            '''
            res = execute_raw_query(query, keyword=f'%{kw[:-1]}%')
        else:
            query = '''
            select count(*)
            from eligible_posts p
            where LOWER(p.caption) like :keyword
            and p.is_deleted = false and p.is_sold = False
            '''
            res = execute_raw_query(query, keyword=f'%{kw}%')
        post_number = res[0][0]
        if post_number < 2:
            continue

        sss_suggestion_pno['keyword'] = kw
        sss_suggestion_pno['post_number'] = post_number
        filter_sss_suggestion.append(sss_suggestion_pno.copy())
    
    filter_sss_suggestion = sorted(filter_sss_suggestion, key=lambda f: f['post_number'], reverse=True)
    # random.shuffle(filter_sss_suggestion)
    # filter_sss_suggestion = filter_sss_suggestion[:6]
    filter_sss_suggestion = [kw_dict['keyword'] for kw_dict in filter_sss_suggestion]

    recent_keywords, popular_keywords, sss_keywords = order_selection([recent_keywords, selected_keywords, filter_sss_suggestion],
                                                                         [0.2, 0.4, 0.4], number_of_suggestion)
    if len(recent_keywords) > 10:
        recent_keywords = recent_keywords[:10]
    if len(popular_keywords) > 6:
        random.shuffle(popular_keywords)
        popular_keywords = popular_keywords[:6]
    if len(sss_keywords) > 6:
        random.shuffle(sss_keywords)
        sss_keywords = sss_keywords[:6]

    # Get popular thumbnails by solr
    popular_pids, popular_thumbnails_url = get_thumbnails_solr(popular_keywords, filter_args=filter_args, limit=len(popular_keywords))
    # popular_thumbnails = []
    # for url in popular_thumbnails_url:
        # bytes_img = minio_download_to_bytes(url)
        # popular_thumbnails.append(bytes_img)
    
    # Get sss thumbnails by config
    keyword_sss_suggestion_url = CONST_MAP.keyword_sss_suggestion_url
    keyword_sss_suggestion_url = [keyword_sss_suggestion_url[i] for i in sss_keywords if i in keyword_sss_suggestion_url.keys()]
    sss_thumbnails_url = []
    for url in keyword_sss_suggestion_url:
        sss_thumbnails_url.append(minio_s3_presign_url(url))
    # sss_thumbnails = []
    # for url in sss_thumbnails_url:
    #     bytes_img = minio_download_to_bytes(url)
    #     sss_thumbnails.append(bytes_img)

    # # Fix boot to boots suggest keyword
    # if 'bootwear' in sss_keywords:
    #     index = sss_keywords.index('bootwear')
    #     sss_keywords[index] = 'bootswear'

    return [
        {
            'text': 'Tìm kiếm gần đây',
            'keywords': recent_keywords
        },
        {
            'text': ' Top tìm kiếm',
            'keywords': popular_keywords,
            'thumbnails': popular_thumbnails_url
        },
        {
            'text': 'SSSMarket gợi ý',
            'keywords': sss_keywords,
            'thumbnails': sss_thumbnails_url
        }
    ]


