import random
from typing import Any
from collections import defaultdict

from src.const.global_map import RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_s3_presign_url
from src.utils.redis_caching import redis_cache_list, redis_cache_json


shoes = [
    "media/virtual_fitting/dummy/shoe_137222.png",
    "media/virtual_fitting/dummy/shoe_15517.png",
    "media/virtual_fitting/dummy/shoe_219315.png",
    "media/virtual_fitting/dummy/shoe_271391.png"
]
shoes = [minio_s3_presign_url(key) for key in shoes]

accessories = [
    "media/virtual_fitting/dummy/accessories_121116.png",
    "media/virtual_fitting/dummy/accessories_242572.png",
    "media/virtual_fitting/dummy/accessories_308052.png",
    "media/virtual_fitting/dummy/accessories_16740.png",
    "media/virtual_fitting/dummy/accessories_247660.png",
    "media/virtual_fitting/dummy/accessories_317288.png",
    "media/virtual_fitting/dummy/accessories_167928.png",
    "media/virtual_fitting/dummy/accessories_250439.png",
    "media/virtual_fitting/dummy/accessories_3753.png",
    "media/virtual_fitting/dummy/accessories_186939.png",
    "media/virtual_fitting/dummy/accessories_271039.png",
    "media/virtual_fitting/dummy/accessories_41118.png",
    "media/virtual_fitting/dummy/accessories_193258.png",
    "media/virtual_fitting/dummy/accessories_274080.png",
    "media/virtual_fitting/dummy/accessories_41761.png"
]
accessories = [minio_s3_presign_url(key) for key in accessories]

shoes_pids = [int(_.split("/")[-1].split(".")[0].split("_")[-1]) for _ in shoes]
accessories_pids = [int(_.split("/")[-1].split(".")[0].split("_")[-1]) for _ in accessories]


# @redis_cache_list(lambda uid, mid: 'vf:uid_%s:mid_%s' % (str(uid), str(mid)), expire_secs=3600)
@redis_cache_json(key_maker=lambda uid, mid: 'vf:uid_%s:mid_%s' % (str(uid), str(mid)), expire_secs=1800)
def get_all_virtual_fit(uid: int, mid: int) -> list[dict[str, Any]]:
    query = """
    with vf_table as (
        select id, gender_id, category_id, ai_metadata, user_id 
        from post p
        where 1 = 1
        and is_virtual_fit = true
        and is_public = true
        and is_deleted = false 
        and is_for_sale = true
        and is_sold = false
        --and p.is_stock_available =true
        and ai_metadata -> 'virtual_fit' -> 'data' -> 0 -> 'label_id' is not null
        and id not in (
            select w.post_id 
            from wishlist w
            where 1 = 1
            and w.user_id in (82, 182, 231074)        
        )
    )
    select vf.id, vf.gender_id, vf.category_id, vf.ai_metadata -> 'virtual_fit' -> 'data', au.account_level_id 
    from vf_table vf
    left join account_user au on vf.user_id = au.id
    where 1 = 1
    --and au.account_level_id is not null
    order by au.id in (select id from top_sellers) desc, coalesce(au.account_level_id, 0) desc
    """
    res = execute_raw_query(query)
    pids_per_cate = defaultdict(list)
    urls_per_cate = defaultdict(list)

    for r in res:
        if r[1] != CONST_MAP.model_gender[mid]:
            if r[1] == 3:
                pass
            else:
                continue

        urls = [_["image_path"] for _ in r[3] if _["model_id"] == mid]
        if len(urls) <= 0:
            continue

        vf_cid = r[3][0]["label_id"]
        if r[2] is not None:
            if r[2] not in CONST_MAP.DB_DETECT_CATEGORY_ID_MAPPING:
                continue
            d_cid = random.choice(CONST_MAP.DB_DETECT_CATEGORY_ID_MAPPING[r[2]])
            if vf_cid not in CONST_MAP.VF_DETECT_CATEGORY_ID_MAPPING_PARALLEL[d_cid]:
                continue
        else:
            d_cid = vf_cid
        vf_cid = CONST_MAP.VF_DETECT_CATEGORY_ID_MAPPING[r[3][0]["label_id"]]

        pids_per_cate[vf_cid].append(r[0])
        urls_per_cate[vf_cid].extend(urls)

    pids_per_cate.default_factory = None
    urls_per_cate.default_factory = None

    data = []
    for k, v in pids_per_cate.items():
        post_urls = [minio_s3_presign_url(_) for _ in urls_per_cate[k]]
        c = list(zip(v, post_urls))
        random.shuffle(c)
        v_shuffle, post_urls_shuffle = zip(*c)

        data.append({
            "position_type": CONST_MAP.VF_POSITION_MAPPING[k],
            "type": CONST_MAP.DETECT_CLOTHING_LABELS_EN[k],
            "name": CONST_MAP.DETECT_CLOTHING_LABELS_VN[k],
            "discovery": {
                "post_ids": v,
                "post_urls": post_urls,
                "positions": [[0, 0, 1280, 853]] * len(v)
            },
            "saved": {
                "post_ids": v_shuffle,
                "post_urls": post_urls_shuffle,
                "positions": [[0, 0, 1280, 853]] * len(v)
            }
        })

    data.extend([{
        "position_type": 0,
        "type": "shoes",
        "name": "giày",
        "discovery": {
            "post_ids": shoes_pids,
            "post_urls": shoes,
        },
        "saved": {
            "post_ids": shoes_pids,
            "post_urls": shoes,
        }
    }, {
        "position_type": 0,
        "type": "accessories",
        "name": "phụ kiện",
        "discovery": {
            "post_ids": accessories_pids,
            "post_urls": accessories,
        },
        "saved": {
            "post_ids": accessories_pids,
            "post_urls": accessories,
        }
    }])

    order_priorities = ["skirt", "pants", "jacket", "top_t-shirt_sweatshirt", "dress", "accessories", "shoes"]
    reorder_data = []
    for k in order_priorities:
        for _ in data:
            if k == _["type"]:
                reorder_data.append(_)

    return reorder_data


def get_post_virtual_fit(uid: int, mid: int, pid: int) -> list[dict[str, Any]]:
    query = """
    select id, gender_id, category_id, ai_metadata -> 'virtual_fit' -> 'data' 
    from post p
    where 1 = 1
    and id in :pid
    """
    res = execute_raw_query(query, pid=tuple([pid]))
    pids_per_cate = defaultdict(list)
    urls_per_cate = defaultdict(list)

    for r in res:
        if r[1] != CONST_MAP.model_gender[mid]:
            if r[1] == 3:
                pass
            else:
                continue

        urls = [_["image_path"] for _ in r[3] if _["model_id"] == mid]
        if len(urls) <= 0:
            continue

        vf_cid = r[3][0]["label_id"]
        if r[2] is not None:
            if r[2] not in CONST_MAP.DB_DETECT_CATEGORY_ID_MAPPING:
                continue
            d_cid = random.choice(CONST_MAP.DB_DETECT_CATEGORY_ID_MAPPING[r[2]])
            if vf_cid not in CONST_MAP.VF_DETECT_CATEGORY_ID_MAPPING_PARALLEL[d_cid]:
                continue
        else:
            d_cid = vf_cid
        vf_cid = CONST_MAP.VF_DETECT_CATEGORY_ID_MAPPING[r[3][0]["label_id"]]

        pids_per_cate[vf_cid].append(r[0])
        urls_per_cate[vf_cid].extend(urls)

    pids_per_cate.default_factory = None
    urls_per_cate.default_factory = None

    data = []
    if len(pids_per_cate) == 0:
        return data

    for k, v in pids_per_cate.items():
        post_urls = [minio_s3_presign_url(_) for _ in urls_per_cate[k]]

        data.append({
            "position_type": CONST_MAP.VF_POSITION_MAPPING[k],
            "type": "try_on",
            "name": "Đồ đang thử",
            "discovery": {
                "post_ids": v,
                "post_urls": post_urls,
                "positions": [[0, 0, 1280, 853]] * len(v)
            },
            "saved": {
                "post_ids": v,
                "post_urls": post_urls,
                "positions": [[0, 0, 1280, 853]] * len(v)
            }
        })

    return data
