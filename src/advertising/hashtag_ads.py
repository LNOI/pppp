import unicodedata
import datetime
import random

from src.advertising.ads_util import get_ads_acc, get_post_from_ads_acc
from src.popular.get_popular import get_uncache_hashtag, get_cachable_hashtag
from src.utils.db_utils import execute_raw_query
from src.const import const_map as CONST_MAP
from src.utils.redis_caching import redis_cache_value, redis_cache_list, redis_cache_json


def gen_ads_hashtag(ads_acc):
    query = '''
    select p.id, p.user_id 
    from top_posts p
    where p.user_id in :ads_acc
    order by random()
    limit :limit
    '''

    ads_post = execute_raw_query(query, ads_acc=tuple(ads_acc), limit=CONST_MAP.post_limit_small)
    # ads_post = [int(i[0]) for i in res]
    post_shop_map = {}
    for pid, sid in ads_post:
        shop_id = int(sid)
        if shop_id not in post_shop_map:
            post_shop_map[shop_id] = []
        post_id = int(pid)
        post_shop_map[shop_id].append(post_id)

    shop_ids = list(post_shop_map.keys())

    if len(shop_ids) > 0:
        # for i in range(len(shop_ids)):
        # random.shuffle(shop_ids)
        sss_id_query = '''select au.id, au.sss_id 
        from top_sellers au 
        where au.id in :shop_ids
        order by array_position(ARRAY[%s]::int[], au.id)''' % ','.join(['%s' % id for id in shop_ids])
        res = execute_raw_query(sss_id_query, shop_ids=tuple(shop_ids))
        sss_ids = [str(i[1]) for i in res]
        shop_hashtag = []
        for shop_id, sss_id in zip(shop_ids, sss_ids):
            shop_hashtag.append(
                {
                    'id': None,
                    'hashtag': '#%s' % sss_id,
                    'post_ids':post_shop_map[shop_id], 
                    'subtitle':'được tài trợ'
                }
            )
        return shop_hashtag
    else:
        return []


@redis_cache_json(key_maker=lambda: 'ads_hashtag', expire_secs=1800)
def get_ads_hashtag(user_id=-1):
    ads_acc = get_ads_acc(no_acc=CONST_MAP.ads_hashtag_slot, ads_type='hashtag')
    if ads_acc:
        ads_hashtag = gen_ads_hashtag(ads_acc)
        return ads_hashtag
    else:
        return []


