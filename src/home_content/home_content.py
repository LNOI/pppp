import numpy as np
import json
import time
import datetime
import random
import logging
from functools import partial
from ast import literal_eval

import src.home_content.utility_carousel
import src.home_content.tab_frame_component
import src.home_content.shop_component
import src.home_content.search_component
import src.home_content.hashtag_component
import src.home_content.banner_component
import src.home_content.event_component
import src.home_content.livestream_component

from src.common.more_utils import get_user_gender_id
from src.home_content.shop_component import PersonalizeShopComponent
from src.recommendation.utils.recsys_scoring import get_new_post_scores, get_user_vector_bytes
from src.utils.db_utils import execute_raw_query

from src.utils.redis_caching import set_redis_json_value, get_redis_json_value
from src.const.global_map import RESOURCE_MAP, HOME_COMPONENT_MAP
from src.const import const_map as CONST_MAP
from src.advertising.hashtag_ads import get_ads_hashtag
from src.advertising.shop_ads import get_ads_shop  

err_logger = logging.getLogger('error_logger')


# import to force register the component class
def placeholder_file_name(index: int, male_item=False) -> str:
    if male_item is True:
        return 'resource/home_placeholder_%s_male.json' % index
    return 'resource/home_placeholder_%s.json' % index


def redis_query_user_vector(key):
    # Query vector on redis cache
    byte_value = RESOURCE_MAP['redis_conn'].get(key)
    if byte_value is not None:
        vec = np.frombuffer(byte_value, dtype=float).reshape(-1)
    else:
        vec = np.ones((CONST_MAP.embed_post_size,))
    return vec


def home_cache_key(index: int, male_item=False) -> str:
    # get basic home cache key (v1711 means 17/11/2021)
    if male_item is True:
        return 'cache_home_content_v1711:male:%s' % index
    else:
        return 'cache_home_content_v1711:%s' % index


def seed_home_cache_key(index: int, male_item=False, test_user=False) -> str:
    if CONST_MAP.test_mode==True and test_user==True:
        # index = 216
        if male_item is True:
            return 'test_cache_home_content:male:%s' % index
        else:
            return 'test_cache_home_content:%s' % index
    else:
        # get seed home cache key (v1212 means 12/12/2021, but v1212:male was 10/2/2022)
        if male_item is True:
            # return 'cache_home_content_v1711:male:%s' % index
            return 'cache_home_content:male:%s' % index
        else:
            return 'cache_home_content:%s' % index


def merchandise_home_cache_key(index: int, male_item=False, test_user=False) -> str:
    if CONST_MAP.test_mode==True and test_user==True:
        index = 216
        if male_item is True:
            return 'test_cache_merchandise_home_content:male:%s' % index
        else:
            return 'test_cache_merchandise_home_content:%s' % index
    else:
        # get merchandise home cache key add on 14/3/2022
        if male_item is True:
            # return 'cache_home_content_v1711:male:%s' % index
            return 'cache_merchandise_home_content:male:%s' % index
        else:
            return 'cache_merchandise_home_content:%s' % index


def get_merchandise_home(user_id: int, male_item=False, test_user=False):
    # Remove index because we wont use cache merchandise content (directly render everytime we use)
    decoded_content = render_single_merchandise_home_content(user_id, male_item, test_user=True)
    return decoded_content


def get_banner_content(user_id: int):
    pass
    # make sure atleast one profile existed in cache
    if RESOURCE_MAP['redis_conn'].exists(seed_home_cache_key(index=0, male_item=True, test_user=False)) == False:
        # refresh_single_seeded_home_content(index)
        raise Exception('Home cache is not exist, load placeholder Home.')

    # getting data
    raw_content = RESOURCE_MAP['redis_conn'].get(seed_home_cache_key(index=0, male_item=True, test_user=False))
    decoded_content = json.loads(raw_content.decode('utf-8'))

    return decoded_content, 0


def get_segment_home_content(user_id: int, index=None):
    gender_id = get_user_gender_id(user_id)
    # the logic here is if the gender is 1 male or 3 unisex, it will show male items
    male_item = not (gender_id == 2)

    if user_id in CONST_MAP.home_api_merchandise_user:
        try:
            return get_merchandise_home(user_id, male_item=male_item), 'merchandise_no_index'
        except Exception as e:
            if male_item:
                place_holder_file = 'resource/merchandise_home_placeholder_male.json'
            else:
                place_holder_file = 'resource/merchandise_home_placeholder_female.json'
            with open(place_holder_file) as f:
                decoded_content = json.load(f)
            return decoded_content, 'merchandise_no_index'
    
    # # Only Test user can use personalize feature
    # if user_id in CONST_MAP.home_api_test_user:
    #     if male_item is True:
    #         decoded_content, index = get_nearest_cached_content(
    #             user_id, index=index, male_item=male_item, test_user=True)
    #     else:
    #         decoded_content, index = get_nearest_cached_content(
    #             user_id, index=index, test_user=True)
    # else:
    #     if male_item is True:
    #         decoded_content, index = get_nearest_cached_content(
    #             user_id, index=index, male_item=male_item, test_user=False)
    #     else:
    #         decoded_content, index = get_nearest_cached_content(
    #             user_id, index=index, test_user=False)
    
    if user_id in CONST_MAP.home_api_test_user:
        if male_item is True:
            decoded_content, index = get_random_cached_content(index=index, male_item=male_item, test_user=True)
        else:
            decoded_content, index = get_random_cached_content(index=index, test_user=True)
    else:
        if male_item is True:
            decoded_content, index = get_random_cached_content(index=index, male_item=male_item, test_user=False)
        else:
            decoded_content, index = get_random_cached_content(index=index, test_user=False)
    # try:
    #     # Render Home component personalized content
    #     # event_text_comp = HOME_COMPONENT_MAP['empty_title_hashtag'](
    #     #     title='Tin nổi bật')
    #     # feature_text_comp = HOME_COMPONENT_MAP['empty_title_hashtag'](
    #     #     title='Tính năng mới')
    #     # decoded_content.insert(1, feature_text_comp.render())
    #     # decoded_content.insert(0, event_text_comp.render())
    #     for comp_name, position in CONST_MAP.home_personalize_components:
    #         comp = HOME_COMPONENT_MAP[comp_name](user_id=user_id, male_item=male_item).render()
    #         decoded_content.insert(position, comp)
    # except Exception as e:
    #     err_logger.error('Create home component %s failed: %s' %
    #                     ('personalize hashtag', str(e)), exc_info=True)

    try:   
        # if CONST_MAP.test_mode == True and user_id in CONST_MAP.home_api_test_user:
        # Get Advertising hashtag
        ads_hashtag = get_ads_hashtag()
        # Get Advertising shop
        ads_shop = get_ads_shop()

        for i in range(len(decoded_content)):
            # Catch no ads case
            if len(ads_hashtag + ads_shop) == 0:
                break
        
            if decoded_content[i]['id'] == 'hashtag_hashtag' and len(ads_hashtag) > 0:
                decoded_content[i]["metadata"]['data'][0:0] = ads_hashtag
                for j in range(len(decoded_content[i]["metadata"]['data'])):
                    decoded_content[i]["metadata"]['data'][j]['id'] = f"hashtag_hashtag_{j}"
            
            if decoded_content[i]['id'] == 'shop_shop' and len(ads_shop) > 0:
                decoded_content[i]["metadata"]['data'][0:0] = ads_shop
                for j in range(len(decoded_content[i]["metadata"]['data'])):
                    decoded_content[i]["metadata"]['data'][j]['id'] = f"shop_shop_{j}"

    except Exception as e:
        err_logger.error('Create home component %s failed: %s' %
                ('ads hashtag/shop', str(e)), exc_info=True)

    for i in range(len(decoded_content)):
        decoded_content[i]['index'] = i

    return decoded_content, index


def get_random_cached_content(male_item=False, index=None, test_user=False):
    # get random cache index (faster)
    if index is None:
        index = random.randint(0, CONST_MAP.home_api_different_random_cache_number-1)

    if RESOURCE_MAP['redis_conn'].exists(seed_home_cache_key(index, male_item, test_user)) is False:
        # refresh_single_home_content(index, male_item)
        raise Exception('Home cache is not exist, load placeholder Home.')

    raw_content = RESOURCE_MAP['redis_conn'].get(seed_home_cache_key(index, male_item, test_user))
    decoded_content = json.loads(raw_content.decode('utf-8'))
    return decoded_content, index


def get_nearest_cached_content(user_id, index=None, male_item=False, test_user=False):
    # get nearest distant cache index (slower)
    if index is None:
        user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
        # Add Male/Female flag for more accurate query active user
        # active_users, active_user_vector = get_active_user_vector(male_item=male_item)
        # Get active user v2
        active_users, active_user_vector = get_active_user_vector_v2(male_item=male_item)
        input_tuple = [(i, active_user_vector[i]) for i in range(len(active_user_vector))]
        score_map = get_new_post_scores(input_tuple, user_vector)
        index = max(score_map, key=score_map.get)

    # make sure atleast one profile existed in cache
    if RESOURCE_MAP['redis_conn'].exists(seed_home_cache_key(index, male_item, test_user)) == False:
        # refresh_single_seeded_home_content(index)
        if test_user:
            # refresh_single_seeded_home_content(index, male_item, test_user=True)
            raise Exception('Home cache is not exist, load placeholder Home.')
        else:
            # refresh_single_seeded_home_content(index, male_item, test_user=False)
            raise Exception('Home cache is not exist, load placeholder Home.')
        # should raise error and rebuild all home profile. Buidling one profile just help this functions
        # normally, rather than solve the problem.
        # -> tricky code, need improvement

    # getting data
    raw_content = RESOURCE_MAP['redis_conn'].get(seed_home_cache_key(index, male_item, test_user))
    decoded_content = json.loads(raw_content.decode('utf-8'))
    return decoded_content, index


def get_placeholder_content(index=None, male_item=False):
    # if get_segment_home_content() fails, return this placeholder
    if index is None:
        index = random.randint(
            0, CONST_MAP.home_api_different_random_cache_number-1)
    with open(placeholder_file_name(index, male_item)) as f:
        decoded_content = json.load(f)
    return decoded_content, index


def refresh_home_content():
    print('#Male item')
    comps = []
    for comp_name in CONST_MAP.home_common_components:
        s = time.time()
        comps.append(HOME_COMPONENT_MAP[comp_name](male_item=True))
        print('%s: %s' % (comp_name, time.time() - s))
    for i in range(CONST_MAP.home_api_different_random_cache_number):
        res = [comp.render() for comp in comps]
        set_redis_json_value(res, 'cache_home_content_v1711:male:%s' % i, expire_secs=3600*24*7)
        with open(placeholder_file_name(i, True), 'w') as f:
            json.dump(res, f)
        print(i)
    print('#Female item')
    comps = []
    for comp_name in CONST_MAP.home_common_components:
        s = time.time()
        comps.append(HOME_COMPONENT_MAP[comp_name]())
        print('%s: %s' % (comp_name, time.time() - s))
    for i in range(CONST_MAP.home_api_different_random_cache_number):
        res = [comp.render() for comp in comps]
        set_redis_json_value(res, 'cache_home_content_v1711:%s' % i, expire_secs=3600*24*7)
        with open(placeholder_file_name(i), 'w') as f:
            json.dump(res, f)
        print(i)


def refresh_single_home_content(index: int, male_item: bool):
    if male_item:
        print('#Male item')
        comps = [HOME_COMPONENT_MAP[comp_name](
            male_item=male_item) for comp_name in CONST_MAP.home_common_components]
        res = [comp.render() for comp in comps]
        set_redis_json_value(
            res, 'cache_home_content_v1711:male:%s' % index, expire_secs=3600*24*7)
        with open(placeholder_file_name(index, True), 'w') as f:
            json.dump(res, f)
        print(index)
    else:
        print('#Female item')
        comps = [HOME_COMPONENT_MAP[comp_name]()
                 for comp_name in CONST_MAP.home_common_components]
        res = [comp.render() for comp in comps]
        set_redis_json_value(res, 'cache_home_content_v1711:%s' %
                             index, expire_secs=3600*24*7)
        with open(placeholder_file_name(index), 'w') as f:
            json.dump(res, f)
        print(index)


# New refresh_seeded with gender
# Seeded_home_content will get some active user (seed user) and render home_content based on these user data
def refresh_seeded_home_content(user_id=82):
    print(f"\n[REFRESH DATE]: {datetime.datetime.now()}")
    weekday = datetime.datetime.now().strftime('%A')
    # CONST_MAP.home_seed_components = ['personalize_shop' if comp =='common_shop' else comp for comp in CONST_MAP.home_events_components.copy()]
    # target_components = CONST_MAP.home_seed_components
    def remove_comp(target_components: list, remove_components: list):
        for comp in remove_components:
            if comp in target_components:
                target_components.remove(comp)

    if weekday in ['Monday', 'Tuesday', 'Thurday', 'Saturday', 'Sunday']:
        CONST_MAP.home_seed_components = ['personalize_shop' if comp =='common_shop' else comp for comp in CONST_MAP.home_events_components.copy()]
        target_components = CONST_MAP.home_seed_components
        if weekday == 'Monday':
            remove_components = ['sssmall_tabframe_t3', 'sfashionn_tabframe_t7_cn']
        elif weekday == 'Tuesday':
            remove_components = ['camp_tabframe_t2', 'sfashionn_tabframe_t7_cn']
        elif weekday == 'Thurday':
            remove_components = ['camp_tabframe_t2', 'sssmall_tabframe_t3', 'sfashionn_tabframe_t7_cn']
        elif weekday == 'Saturday':
            remove_components = ['camp_tabframe_t2', 'sssmall_tabframe_t3']
        elif weekday == 'Sunday':
            remove_components = ['camp_tabframe_t2', 'sssmall_tabframe_t3']
        else:
            raise 'Unsupport weekday...'
        
        remove_comp(target_components, remove_components)

    else:
        CONST_MAP.home_seed_components = ['personalize_shop' if comp =='common_shop' else comp for comp in CONST_MAP.home_common_components.copy()]
        target_components = CONST_MAP.home_seed_components

    print('Start refresh seeded home content for both gender.')
    if user_id in CONST_MAP.home_api_test_user and CONST_MAP.test_mode == True:
        print("[CHECK] - Refresh seeded home content for [DEV SERVER]")
    print(f"#Refresh seeded Male home content.")
    # active_users, active_user_vector = get_active_user_vector(force_refresh=True, male_item=True)
    active_users, active_user_vector = get_active_user_vector_v2(force_refresh=True, male_item=True)
    for i in range(len(active_user_vector)):
        seed_uid = active_users[i]
        print('Start create %s: user %s' % (i, seed_uid))
        seed_vec = active_user_vector[i]
        comps = [HOME_COMPONENT_MAP[comp_name](
            user_id=seed_uid, user_vec=seed_vec, male_item=True) for comp_name in target_components]
        
        res = [comp.render() for comp in comps]
        with open(placeholder_file_name(i, True), 'w') as f:
            json.dump(res, f)
        
        # If create test home cache change "cache_home_content" to "test_cache_home_content"
        if user_id in CONST_MAP.home_api_test_user and CONST_MAP.test_mode == True:
            set_redis_json_value(res, 'test_cache_home_content:male:%s' % i, expire_secs=3600*24*3)
        else:
            set_redis_json_value(res, 'cache_home_content:male:%s' % i, expire_secs=3600*24*3)
        print('End create %s: user %s\n' % (i, seed_uid))

    print('\n')

    print(f"#Refresh seeded Female home content.")
    # active_users, active_user_vector = get_active_user_vector(force_refresh=True, male_item=False)
    active_users, active_user_vector = get_active_user_vector_v2(force_refresh=True, male_item=False)
    for i in range(len(active_user_vector)):
        seed_uid = active_users[i]
        print('Start create %s: user %s' % (i, seed_uid))
        seed_vec = active_user_vector[i]
        comps = [HOME_COMPONENT_MAP[comp_name](
            user_id=seed_uid, user_vec=seed_vec) for comp_name in target_components]
        
        res = [comp.render() for comp in comps]
        
        with open(placeholder_file_name(i, False), 'w') as f:
            json.dump(res, f)
        
        # If create test home cache change "cache_home_content" to "test_cache_home_content"
        if user_id in CONST_MAP.home_api_test_user and CONST_MAP.test_mode == True:
            set_redis_json_value(res, 'test_cache_home_content:%s' % i, expire_secs=3600*24*3)
        else:
            set_redis_json_value(res, 'cache_home_content:%s' % i, expire_secs=3600*24*3)
        print('End create %s: user %s\n' % (i, seed_uid))

    print('Done refresh seeded home content for both gender.\n')
    return "Finish Home Cache Refresh"


def refresh_single_seeded_home_content(index: int, male_item: bool, test_user: bool):
    if CONST_MAP.test_mode==True and test_user==True:
        if male_item:
            active_users, active_user_vector = get_active_user_vector(force_refresh=True, male_item=male_item)
            seed_uid = active_users[index]
            seed_vec = active_user_vector[index]
            comps = [HOME_COMPONENT_MAP[comp_name](
                user_id=seed_uid, user_vec=seed_vec, male_item=male_item) for comp_name in CONST_MAP.home_seed_components]
            res = [comp.render() for comp in comps]
            # index = '216'
            set_redis_json_value(res, 'test_cache_home_content:male:%s' % index, expire_secs=3600*24)
        else:
            active_users, active_user_vector = get_active_user_vector(force_refresh=True)
            seed_uid = active_users[index]
            seed_vec = active_user_vector[index]
            comps = [HOME_COMPONENT_MAP[comp_name](
                user_id=seed_uid, user_vec=seed_vec) for comp_name in CONST_MAP.home_seed_components]
            res = [comp.render() for comp in comps]
            # index = '216'
            set_redis_json_value(res, 'test_cache_home_content:%s' % index, expire_secs=3600*24)
        print(index)
        print(f"Done refresh single seeded home content for {index}")
    else:
        if male_item:
            active_users, active_user_vector = get_active_user_vector(force_refresh=True, male_item=male_item)
            seed_uid = active_users[index]
            seed_vec = active_user_vector[index]
            comps = [HOME_COMPONENT_MAP[comp_name](
                user_id=seed_uid, user_vec=seed_vec, male_item=male_item) for comp_name in CONST_MAP.home_seed_components]
            res = [comp.render() for comp in comps]
            set_redis_json_value(res, 'cache_home_content:male:%s' % index, expire_secs=3600*24)
        else:
            active_users, active_user_vector = get_active_user_vector(force_refresh=True)
            seed_uid = active_users[index]
            seed_vec = active_user_vector[index]
            comps = [HOME_COMPONENT_MAP[comp_name](
                user_id=seed_uid, user_vec=seed_vec) for comp_name in CONST_MAP.home_seed_components]
            res = [comp.render() for comp in comps]
            set_redis_json_value(res, 'cache_home_content:%s' %index, expire_secs=3600*24)
        print(index)
        print(f"Done refresh single seeded home content for {index}")


def render_single_merchandise_home_content(user_id: int, male_item: bool, test_user: bool):
    if male_item:
        print('#Male item')
        comps = [HOME_COMPONENT_MAP[comp_name](
            male_item=male_item, user_id=user_id) for comp_name in CONST_MAP.merchandise_components]
        res = [comp.render() for comp in comps]
        with open('resource/merchandise_home_placeholder_male.json', 'w') as f:
            json.dump(res, f)
        return res

    else:
        print('#Female item')
        comps = [HOME_COMPONENT_MAP[comp_name](user_id=user_id)
                 for comp_name in CONST_MAP.merchandise_components]
        res = [comp.render() for comp in comps]
        with open('resource/merchandise_home_placeholder_female.json', 'w') as f:
            json.dump(res, f)
        return res


def get_active_user_vector(force_refresh=False, male_item=False) -> list[np.ndarray]:
    if not force_refresh and 'user_list' in get_active_user_vector.__dict__ and 'vector_list' in get_active_user_vector.__dict__:
        return get_active_user_vector.user_list, get_active_user_vector.vector_list
    else:
        if male_item:
            gen = [1]
        else:
            gen = [2,3]

        query = '''
        select id 
        from account_user au 
        where au.last_online > now() - interval '24 hour'
        and au.gender in :gen
        order by au.last_online desc, (ai_metadata ->> 'user_score')::float desc
        '''

        res = execute_raw_query(query, gen=tuple(gen))
        user_ids = [int(i[0]) for i in res]
        random.shuffle(user_ids)
        user_vec_map = {}
        for user_id in user_ids:
            user_vec = np.frombuffer(get_user_vector_bytes(
                user_id), dtype=float).reshape(-1)
            if not np.array_equal(user_vec, np.ones((CONST_MAP.embed_post_size,))):
                user_vec_map[user_id] = user_vec
            # CONST_MAP.home_api_different_random_cache_number):
            if len(user_vec_map) >= 10:
                break
        
        # Cache in code/app (if restart/die app, lose it)
        selected_user_ids = list(user_vec_map.keys())
        get_active_user_vector.user_list = selected_user_ids
        user_vec_list = list(user_vec_map.values())
        get_active_user_vector.vector_list = user_vec_list

        return selected_user_ids, user_vec_list

def get_active_user_vector_v2(force_refresh=False, male_item=False) -> list[np.ndarray]:
    if male_item:
        active_user_cache = 'cache_active_user:male'
        active_vec_cache = 'cache_active_vec:male'
    else:
        active_user_cache = 'cache_active_user:female'
        active_vec_cache = 'cache_active_vec:female'
    
    if not force_refresh and RESOURCE_MAP['redis_conn'].exists(active_user_cache) and RESOURCE_MAP['redis_conn'].exists(active_vec_cache):
        user_list = get_redis_json_value(active_user_cache)
        vec_list = get_redis_json_value(active_vec_cache)
        vec_list = [np.array(i) for i in vec_list]

        return user_list, vec_list
    else:
        if male_item:
            gen = [1, 3]
        else:
            gen = [2]

        query = '''
        select id 
        from account_user au 
        where au.last_online > now() - interval '24 hour'
        and au.gender in :gen
        order by au.last_online desc, (ai_metadata ->> 'user_score')::float desc
        '''

        res = execute_raw_query(query, gen=tuple(gen))
        user_ids = [int(i[0]) for i in res]
        random.shuffle(user_ids)
        user_vec_map = {}

        for user_id in user_ids:
            user_vec = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
            if not np.array_equal(user_vec, np.ones((CONST_MAP.embed_post_size,))):
                user_vec_map[user_id] = user_vec
            # CONST_MAP.home_api_different_random_cache_number):
            if len(user_vec_map) >= 10:
                break
        
        selected_user_ids = list(user_vec_map.keys())
        selected_user_vecs = list(user_vec_map.values())
        user_vec_list = [i.tolist() for i in selected_user_vecs]
        # Cache in redis
        set_redis_json_value(selected_user_ids, active_user_cache, expire_secs=3600*24)
        set_redis_json_value(user_vec_list, active_vec_cache, expire_secs=3600*24)

        return selected_user_ids, selected_user_vecs
