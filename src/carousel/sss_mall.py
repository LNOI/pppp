from functools import partial

from src.carousel.common import get_content_post_ids, get_user_thubmnail_post_id
from src.common.more_utils import split_post_infos_by_user
from src.utils.redis_caching import redis_cache_json

@redis_cache_json(key_maker=lambda: 'sss_mall:res', expire_secs=3600)
def get_sssmall_user_and_post_ids() -> list[dict]:
    user_ids = get_sss_mall_user()

    res = []
    for user_id in user_ids:
        thumbnail_post_ids = get_user_thubmnail_post_id(user_id)
        post_ids = get_content_post_ids(user_id)
        if len(thumbnail_post_ids) > 0:
            res.append({
                'user_id':user_id,
                'thumbnail_post_ids':thumbnail_post_ids,
                'post_ids':post_ids
            })
    return res

from src.carousel.voucher_post import get_voucher_post_info
@redis_cache_json(key_maker=lambda: 'sss_mall_voucher:res', expire_secs=3600)
def get_sssmall_user_and_post_ids_from_voucher() -> list[dict]:
    post_infos = get_voucher_post_info()
    shop_pi_map = split_post_infos_by_user(post_infos)
    
    res = []
    for shop_id in shop_pi_map:
        thumbnail_post_ids = get_user_thubmnail_post_id(shop_id)
        post_ids = [pi.pid for pi in shop_pi_map[shop_id]]
        if len(thumbnail_post_ids) > 0:
            res.append({
                'user_id':shop_id,
                'post_ids':post_ids,
                'thumbnail_post_ids':thumbnail_post_ids
            })
    return res

def get_sssmall_user_and_post_ids_data() -> dict:
    post_infos = get_voucher_post_info()
    shop_pi_map = split_post_infos_by_user(post_infos)
    
    res = {}
    for shop_id in shop_pi_map:
        thumbnail_post_ids = get_user_thubmnail_post_id(shop_id)
        post_ids = [pi.pid for pi in shop_pi_map[shop_id]]
        if len(thumbnail_post_ids) > 0:
            res[shop_id] = [post_ids, thumbnail_post_ids]
    return res

from marshmallow import Schema, fields
from marshmallow.validate import Range

class SSSMallShopSchema(Schema):
    user_id = fields.Integer(strict=True, validate=[Range(min=1)])
    thumbnail_post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]))
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]))

from src.common.source.active_user_source import top_sellers_source, promoted_sellers_source
from src.common.filter.user_sql_filter import is_business_acc, male_acc, female_acc

def get_sss_mall_user(male_item=False):
    filters = []
    # filters.append(is_business_acc)
    if male_item:
        filters.append(male_acc)
    else:
        filters.append(female_acc)
    # user_ids = top_sellers_source(filters)
    user_ids = promoted_sellers_source()
    return user_ids
