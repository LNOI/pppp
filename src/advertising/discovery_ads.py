import random

from src.advertising.ads_util import get_ads_acc, get_post_from_ads_acc
from src.const import const_map as CONST_MAP


"""
    At the present, we do not use this fucntion but change the query in "get_shop_post_info"
"""
def get_ads_discovery(post_ids, ads_type: str):
    # Calculate number of ads based on 20% number of posts
    no_ads = int(len(post_ids) * CONST_MAP.ads_discovery_4you)
    if no_ads == 0:
        no_ads = 2
    ads_post = get_post_from_ads_acc(no_post=no_ads, ads_type=ads_type)

    post_ids.extend(ads_post)
    random.shuffle(post_ids)

    return post_ids


