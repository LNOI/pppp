from src.utils.db_utils import execute_raw_query


def check_ads_type(ads_type: str):
    # pass
    # return [3]
    if ads_type == 'hashtag':
        return [21, 22, 23, 24, 25]
    elif ads_type == 'search':
        return [22, 23, 24, 25]
    elif ads_type == 'shop4you':
        return [23, 24, 25]
    elif ads_type == 'discovery_4you':
        return [23, 24, 25]
    elif ads_type == 'discovery_trending':
        return [24, 25]

    else:
        raise TypeError("Unsupport Adsvertisement type.")


def get_ads_acc(no_acc: int, ads_type: str, uids=[]):
    ads_object = check_ads_type(ads_type=ads_type)

    if ads_type == 'search':
        query = '''
        select es.id
        from top_sellers es 
        where 1=1
        and es.account_level_id in :ads_object --(3)--(21,22,23,24)
        and es.id in :uids
        order by random() * (account_level_id - 20)
        limit :limit 
        '''
        res = execute_raw_query(query, limit=no_acc, ads_object=tuple(ads_object), uids=tuple(uids))
        ads_accounts = [int(i[0]) for i in res]
        return ads_accounts
    else:
        query = '''
        select es.id
        from top_sellers es 
        where 1=1
        and es.account_level_id in :ads_object --(3)--(21,22,23,24)
        and es.total_posts > 0
        order by random() * (account_level_id - 20)
        limit :limit 
        '''
        res = execute_raw_query(query, limit=no_acc, ads_object=tuple(ads_object))
        ads_accounts = [int(i[0]) for i in res]
        return ads_accounts


def get_post_from_ads_acc(no_post: int, ads_type: str, pids=[]):
    ads_object = check_ads_type(ads_type=ads_type)
    
    if ads_type == 'search':
        query = '''
        with rank_table as (
            select row_number() over (partition by pop.user_id order by random() * (pop.ai_metadata->'post_score'->'total')::numeric desc) as r, pop.*
            from top_posts pop 
            Where 1=1
            and pop.account_level_id in :ads_object --(3) --(22,23,24)
            --pop.account_level_id in (23,24)
            and pop.id in :pids
        )
        select id
        from rank_table
        where r = 1
        order by random() * (account_level_id - 20)
        limit :limit
        '''
        res = execute_raw_query(query, limit=no_post, ads_object=tuple(ads_object), pids=tuple(pids))
        ads_posts = [int(i[0]) for i in res]
        return ads_posts
    else:
        query = '''
        with rank_table as (
            select row_number() over (partition by pop.user_id order by random() * (pop.ai_metadata->'post_score'->'total')::numeric desc) as r, pop.*
            from top_posts pop 
            Where 1=1
            and pop.account_level_id in :ads_object --(3) --(22,23,24)
            --pop.account_level_id in (23,24)
            -- and pop.id in :pids
        )
        select id
        from rank_table
        where r = 1
        order by random() * (account_level_id - 20)
        limit :limit
        '''
        res = execute_raw_query(query, limit=no_post, ads_object=tuple(ads_object))
        ads_posts = [int(i[0]) for i in res]
        return ads_posts


