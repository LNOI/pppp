import logging
import random

from src.const.global_map import RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.recommendation.new_watch_next import matching_user_with_content, matching_user_with_content_redis
from src.recommendation.placeholder_watchnext import  static_placeholder

from src.utils.decorator import anonymous_user
from src.utils.basemodel.response_schemas import create_response
from src.utils.basemodel import discovery_schemas as schemas

from src.api_endpoint.add_api import short_api_log

from fastapi.encoders import jsonable_encoder
from fastapi import Request

logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')

app = RESOURCE_MAP['fastapi_app']

'''
    Lightweight content in case of light_mode and not enough posts from sources
'''
def redis_dummy_content_with_filter(gender_ids: list=[2], no_discovery: int=10) -> list:
    # low computation mode
    final_results = matching_user_with_content_redis(discovery_type='mall')

    # sex filtering, by pass all requirement
    if gender_ids:
        if gender_ids == [1]:
            post_ids = final_results[0]
        elif gender_ids == [1, 2]:
            post_ids = final_results[0] + final_results[1]
        else:
            post_ids = final_results[1]
    else:
        post_ids = final_results[0] + final_results[1]

    # resulting    
    random.shuffle(post_ids)
    post_ids = post_ids[:no_discovery]

    return post_ids


'''
This function is to recommend posts from mall for discovery section
Mall: account_level_id 21-25
'''

@app.post('/discovery_mall')
@short_api_log
async def discovery_mall(input_map:schemas.DiscoverySchema, request : Request):
    #init
    user_id = None
    no_watch_next = None

    try:
        # parsing input map
        input_map = jsonable_encoder(input_map)
        # logger.info('%s: Recommend personalize request: start: %s' % (request.remote_addr, str(input_map)))
        user_id = input_map['user_id']
        no_watch_next = input_map['no_watch_next']
        
        filter_args = {
            'user_id':user_id,
            "category": [],
            "size": [],
            "condition": [],
            "sex": [],
            "price": []
        }
        if 'filter' in input_map:
            if 'category' in input_map['filter']:
                filter_args['category'] = input_map['filter']['category']
            if 'size' in input_map['filter']:
                filter_args['size'] = input_map['filter']['size']
            if 'condition' in input_map['filter']:
                filter_args['condition'] = input_map['filter']['condition']
            if 'price' in input_map['filter'] and len(input_map['filter']['price']) == 2:
                filter_args['price'] = [int(i*10000) for i in input_map['filter']['price']]
            if 'sex' in input_map['filter']:
                filter_args['sex'] = input_map['filter']['sex']
        
        # if not low computation mode
        if not CONST_MAP.light_mode:
            if user_id == -1: # annonymous user
                user_id = anonymous_user(user_id) # dummy user

            # process 
            post_ids = matching_user_with_content(user_id, no_watch_next, 'discovery_mall', filter_args)   
        else: 
            # low computation mode
            post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)

        if len(post_ids) <= 3:
            deviation_logger.info('Recommended personalize request: User %s:%s post number = 0. Use placeholder. \n' % (user_id, no_watch_next))

            # low computation mode
            dummy_post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)
            
            return create_response(status=200,content=dummy_post_ids)

        logger.info('Recommend personalize request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        return create_response(status=200,content=post_ids)
        
    except Exception as e:
        err_logger.info('Recommendation personalize critical error: %s \n' % str(e), exc_info=True)
        return create_response(status=500,content=static_placeholder())
    
    
'''
This function is to recommend posts from 2hand (si) for discovery section
2hand: conditionally from condition and hashtag
'''
@app.post("/discovery_2hand")
@short_api_log
async def discovery_2hand(input_map:schemas.DiscoverySchema, request: Request):
    #init
    user_id = None
    no_watch_next = None

    try:
        # parsing input map
        input_map = jsonable_encoder(input_map)
        logger.info('%s: Recommend personalize request: start: %s' % (request.client.host, str(input_map)))
        
        user_id = input_map['user_id']
        no_watch_next = input_map['no_watch_next']
                                                                                                                                                                                                                
        filter_args = {
            'user_id':user_id,
            "category": [],
            "size": [],
            "condition": [],
            "sex": [],
            "price": []
        }
        if 'filter' in input_map:
            if 'category' in input_map['filter']:
                filter_args['category'] = input_map['filter']['category']
            if 'size' in input_map['filter']:
                filter_args['size'] = input_map['filter']['size']
            if 'condition' in input_map['filter']:
                filter_args['condition'] = input_map['filter']['condition']
            if 'price' in input_map['filter'] and len(input_map['filter']['price']) == 2:
                filter_args['price'] = [int(i*10000) for i in input_map['filter']['price']]
            if 'sex' in input_map['filter']:
                filter_args['sex'] = input_map['filter']['sex']
        
        # if not low computation mode
        if not CONST_MAP.light_mode:
            if user_id == -1: # annonymous user
                user_id = anonymous_user(user_id) # dummy user

            # process 
            post_ids = matching_user_with_content(user_id, no_watch_next, 'discovery_2hand', filter_args)   
        else: 
            # low computation mode
            post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)

        if len(post_ids) <= 3:
            deviation_logger.info('Recommended personalize request: User %s:%s post number = 0. Use placeholder. \n' % (user_id, no_watch_next))

            # low computation mode
            dummy_post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)
            return create_response(status=200, content=dummy_post_ids)
        
        logger.info('Recommend personalize request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        return create_response(status=200, content=post_ids)
    except Exception as e:
        err_logger.info('Recommendation personalize critical error: %s \n' % str(e), exc_info=True)
        return create_response(status=500, content=static_placeholder())


'''
This function is to recommend posts not from new for discovery section
new: conditionally from condition and hashtag
'''
@app.post('/discovery_new')
@short_api_log
async def discovery_new(input_map:schemas.DiscoverySchema, request: Request):
    #init
    user_id = None
    no_watch_next = None

    try:
        # parsing input map
        input_map = jsonable_encoder(input_map)
        logger.info('%s: Recommend personalize request: start: %s' % (request.client.host, str(input_map)))
        user_id = input_map['user_id']
        no_watch_next = input_map['no_watch_next']

        filter_args = {
            'user_id':user_id,
            "category": [],
            "size": [],
            "condition": [],
            "sex": [],
            "price": []
        }
        if 'filter' in input_map:
            if 'category' in input_map['filter']:
                filter_args['category'] = input_map['filter']['category']
            if 'size' in input_map['filter']:
                filter_args['size'] = input_map['filter']['size']
            if 'condition' in input_map['filter']:
                filter_args['condition'] = input_map['filter']['condition']
            if 'price' in input_map['filter'] and len(input_map['filter']['price']) == 2:
                filter_args['price'] = [int(i*10000) for i in input_map['filter']['price']]
            if 'sex' in input_map['filter']:
                filter_args['sex'] = input_map['filter']['sex']
        
        # if not low computation mode
        if not CONST_MAP.light_mode:
            if user_id == -1: # annonymous user
                user_id = anonymous_user(user_id) # dummy user

            # process 
            post_ids = matching_user_with_content(user_id, no_watch_next, 'discovery_new', filter_args)   
        else: 
            # low computation mode
            post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)

        if len(post_ids) <= 3:
            deviation_logger.info('Recommended personalize request: User %s:%s post number = 0. Use placeholder. \n' % (user_id, no_watch_next))

            # low computation mode
            dummy_post_ids = redis_dummy_content_with_filter(gender_ids=input_map['filter']['sex'], no_discovery=no_watch_next)
            return create_response(status=200, content=dummy_post_ids)

        logger.info('Recommend personalize request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        return create_response(status=200, content=post_ids)
    except Exception as e:
        err_logger.info('Recommendation personalize critical error: %s \n' % str(e), exc_info=True)
        return create_response(status=500, content= static_placeholder())





