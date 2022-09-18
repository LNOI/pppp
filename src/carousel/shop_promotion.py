import random
import numpy as np
import scipy.spatial as spatial

from src.common.filter.post_sql_filter import gender
from src.common.get_style_shop_vector import get_shop_embed_vector
from src.common.random_shuffle import random_shuffle
from src.common.more_utils import get_user_address

from src.recommendation.utils.recsys_scoring import get_user_vector_bytes
from src.const import const_map as CONST_MAP
from src.utils.db_utils import execute_raw_query
from src.carousel.sss_mall import get_sss_mall_user



def get_common_promoted_shop(number_of_shop: int, male_item: bool) -> list[int]:
    new_shops = query_new_shop()
    shop_scores = [1] * len(new_shops)
    shuffled_new_shops = random_shuffle(new_shops, shop_scores)
    sss_mall_shops = get_sss_mall_user(male_item)

    sss_mall_shops_required_number = 1

    total_shops = [] \
        + sss_mall_shops[:sss_mall_shops_required_number] \
        + shuffled_new_shops \
        + sss_mall_shops[sss_mall_shops_required_number:]
    dedup_total_shops = list(dict.fromkeys(total_shops))
    selected_shops = dedup_total_shops[:number_of_shop]
    return selected_shops


def get_promoted_shop(user_id: int, male_item: bool, number_of_shop: int) -> tuple[list[int], int]:
    sss_mall_shops = get_sss_mall_user(male_item)
    liked_shops = query_liked_shop(user_id)

    sss_mall_shops_required_number = 1
    # random.shuffle(sss_mall_shops)
    random.shuffle(liked_shops)
    total_shops = sss_mall_shops[:sss_mall_shops_required_number] \
        + liked_shops[:3]
    if len(total_shops) < number_of_shop:
        shuffled_top_shops = get_style_similar_shop(user_id, male_item)
        total_shops += shuffled_top_shops + sss_mall_shops[sss_mall_shops_required_number:]
    dedup_total_shops = list(dict.fromkeys(total_shops))
    selected_shops = dedup_total_shops[:number_of_shop]
    return selected_shops, len(set(selected_shops) & set(liked_shops))


def get_weekly_shop(number_of_shop: int, male_item: bool, weekday: str) -> list[int]:
    if male_item:
        gender_ids = [1]
    else:
        gender_ids = [2]

    if weekday == 'Monday':
        pass
        query = '''
        with count_2hand as (	
            select user_id, count(*) as sh_posts
            from top_posts pop 
            where 1=1
            and pop.ai_metadata->>'2hand' = 'true'
            and pop.gender_id in :gender_ids
            group by user_id
        )
        select user_id 
        from count_2hand
        where 1=1
        and sh_posts >= 10
        '''
    elif weekday == 'Tuesday':
        pass
        query = ''''''
    elif weekday == 'Wednesday':
        pass
        query = ''''''
    elif weekday == 'Thursday':
        pass
        query = ''''''
    elif weekday == 'Friday':
        pass
        query = ''''''
    elif weekday == 'Saturday':
        pass
        query = ''''''
    elif weekday == 'Sunday':
        pass
        query = ''''''
    else:
        pass

    shop_ids = [int(i[0]) for i in execute_raw_query(query, gender_ids=tuple(gender_ids))]
    return shop_ids


def query_subsription_shop() -> list[int]:
    query = '''
    select id
    from top_sellers au 
    where account_level_id > 2
    '''
    shop_ids = [int(i[0]) for i in execute_raw_query(query)]
    return shop_ids


def query_new_shop() -> list[int]:
    """
        Not add gender filter due to the low number of new user is male/unisex
    """
    query = '''select af.user_id, count(*) as score
    from account_following af 
    left join eligible_users au on au.id = af.user_id 
    where af.created_at > current_date - interval '1 week'
    -- and au.account_level_id not in (99, 2, 3, 4, 5, 6)
    group by af.user_id
    order by score desc 
    limit 10
    '''
    shop_ids = [int(i[0]) for i in execute_raw_query(query)]
    return shop_ids


def query_consignment_candidates(user_id: int, is_near_by: bool):
    user_addr = get_user_address(user_id, 2)
    nearby = 'not'
    if is_near_by:
        nearby = ''
    query = '''
    with merch_viewed_posted as (
        select t.object_id::int
        from tracing t
        where t."action" = 'view'
        and t.created_at > current_date - interval '1 month'
        and t.actor_id::int in (
            select id
            from account_user au
            where au.account_level_id = 98
        )
    ),
    sample as (
        select p.user_id, count(*) as "total_upload", max(p.created_at) as created_at
        from post p
        where p.created_at > now() - interval '1 month'
        and p.is_public = true
        and p.is_deleted = false
        and p.is_for_sale = true
        and p.id not in (
            select object_id
            from merch_viewed_posted
        )
        group by 1
    ),
    sample_with_aa as (
        select s.*, concat(aa.province, '_', aa.district, '_', aa.ward) as address
        from sample s
        left join account_user au on au.id = s.user_id
        left join account_address aa on aa.id = au.default_address_id
        where total_upload >= 3
        and total_upload <= 10
    )
    select *
    from sample_with_aa
    where address %s like %s
    order by created_at desc
    limit 10
    ''' % (nearby, f"'%{user_addr}%'")
    shop_ids = [int(i[0]) for i in execute_raw_query(query)]
    return shop_ids


def get_style_similar_shop(user_id: int, male_item=False):
    user_vector = np.frombuffer(get_user_vector_bytes(user_id)).reshape(-1)
    user_style_vector = user_vector[-CONST_MAP.style_post_size:]
    top_shops = query_top_shop(male_item)
    top_shops_map = get_shop_embed_vector(top_shops)
    shop_vectors = [top_shops_map[sid] for sid in top_shops]
    shop_scores = [spatial.distance.cosine(user_style_vector, shop_vector) for shop_vector in shop_vectors]
    shuffled_top_shops = random_shuffle(top_shops, shop_scores)
    return shuffled_top_shops


def query_top_shop(male_item=False) -> list[int]:
    if male_item:
        gender = [1]
    else:
        gender = [2, 3]

    query = '''
    select p.user_id, max((p.ai_metadata -> 'post_score' -> 'seller')::float) as seller_score 
    from eligible_posts p
    where p.user_id in (
        select es.id from top_sellers es 
        where es.total_posts > :limit
        and es.gender in :gender
    )
    and p.ai_metadata -> 'post_score' -> 'seller' is not null
    group by p.user_id 
    order by seller_score desc
    limit 40'''
    shop_ids = [int(i[0]) for i in execute_raw_query(
        query, limit=CONST_MAP.shop_component_shop_post_lower_limit, gender=tuple(gender))]
    return shop_ids


def query_liked_shop(user_id: int) -> list[int]:
    query = '''
    with post_liked as (
        select w.post_id, p.user_id 
        from wishlist w 
        left join eligible_posts p on w.post_id = p.id
        left join eligible_users au on p.user_id = au.id
        where w.user_id = :user_id
        and p.user_id not in (
            select af.user_id 
            from account_following af 
            where af.followed_by = :user_id
        )
        and p.user_id in (
            select id 
            from top_sellers es 
            where es.total_posts > :limit
        )
        -- and au.account_level_id not in (99, 2, 3, 4, 5, 6)
    ),
    ranking_table as (
        select user_id, count(*) * random() as score
        from post_liked
        where user_id is not null
        group by user_id
    )
    select user_id
    from ranking_table
    order by score desc 
    limit 3
    '''
    shop_ids = [int(i[0]) for i in execute_raw_query(query, user_id=user_id,
                                                     limit=CONST_MAP.shop_component_shop_post_lower_limit)]
    return shop_ids
