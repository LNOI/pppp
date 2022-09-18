import unicodedata
import datetime
import random

from src.advertising.ads_util import get_ads_acc, get_post_from_ads_acc
from src.popular.get_popular import get_uncache_hashtag, get_cachable_hashtag
from src.utils.db_utils import execute_raw_query
from src.const import const_map as CONST_MAP
from src.home_content.shop_component import get_shop_info, get_content_post_ids, get_user_thubmnail_post_id
from src.utils.redis_caching import redis_cache_value, redis_cache_list, redis_cache_json


# def gen_ads_shop(ads_acc):
#     header = unicodedata.normalize('NFKC','Gợi ý shop')
#     return ads_acc, header


@redis_cache_json(key_maker=lambda: 'ads_shop', expire_secs=1800)
def get_ads_shop():
    ads_acc = get_ads_acc(no_acc=CONST_MAP.ads_shop4you_slot, ads_type='shop4you')    

    if len(ads_acc) > 0:
        shop_infos = get_shop_info(ads_acc)
        titles = [shop_infos[shop_id]['title'] for shop_id in ads_acc]
        avatar_urls = [shop_infos[shop_id]['avatar_url'] for shop_id in ads_acc]
        post_idss = [get_content_post_ids(shop_id) for shop_id in ads_acc]
        thumbnailss = [get_user_thubmnail_post_id(shop_id) for shop_id in ads_acc]

        shop_info = [
            {
                'id': None,
                'title': titles[i],
                'avatar_url': avatar_urls[i],
                'thumbnail_post_ids': thumbnailss[i],
                'post_ids': thumbnailss[i] + [pid for pid in post_idss[i] if pid not in thumbnailss[i]]
            }
            for i in range(len(titles))
        ]

        return shop_info
    else:
        return []


# class AdsShopComponent(BaseShopComponent):
#     def refresh_new_data(self, **kwargs):
#         self.id='shop_shop'
#         self.shop_ids, self.header = get_ads_shop()
#         self.refresh_detail_from_shop_ids()
