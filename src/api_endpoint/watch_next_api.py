import logging
import random
import secrets

from src.const.global_map import RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.recommendation.new_watch_next import matching_user_with_content, matching_user_with_content_redis
from src.recommendation.placeholder_watchnext import filter_placeholder, static_placeholder
from src.api_endpoint.add_api import api_log, short_api_log
from src.advertising.discovery_ads import get_ads_discovery


from src.utils.basemodel import watchnext_schemas as schemas
from src.utils.basemodel.response_schemas import create_response

from fastapi import Request
from fastapi.encoders import jsonable_encoder
logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')

app = RESOURCE_MAP['fastapi_app']


@app.post('/watch_next_trending' )
@short_api_log
async def trend_recommend(input_map: schemas.WatchnextSchema, request: Request):
    user_id = None
    no_watch_next = None
    filter_args = {
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }

    try:
        input_map = jsonable_encoder(input_map)
        logger.info('%s: Recommend trend request: start: %s' % (request.client.host, str(input_map)))
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

        if not CONST_MAP.light_mode:
            if user_id == 130381: # Acc thaomy, of team curator
                post_ids = matching_user_with_content(user_id, no_watch_next, 'manual_select_keyword', filter_args)
            
            elif user_id == -1:
                final_results = matching_user_with_content_redis(discovery_type='trending')
                if input_map['filter']['sex']:
                    if input_map['filter']['sex'] == [1]:
                        post_ids = final_results[0]
                    elif input_map['filter']['sex'] == [1, 2]:
                        post_ids = final_results[0] + final_results[1]
                    else:
                        post_ids = final_results[1]
                else:
                    post_ids = final_results[0] + final_results[1]
                random.shuffle(post_ids)
            
            else:
                post_ids = matching_user_with_content(user_id, no_watch_next, 'trending', filter_args)
        else:
            final_results = matching_user_with_content_redis(discovery_type='trending')
            if input_map['filter']['sex']:
                if input_map['filter']['sex'] == [1]:
                    post_ids = final_results[0]
                elif input_map['filter']['sex'] == [1, 2]:
                    post_ids = final_results[0] + final_results[1]
                else:
                    post_ids = final_results[1]
            else:
                post_ids = final_results[0] + final_results[1]
            random.shuffle(post_ids)
        
        if len(post_ids) <= 0:
            deviation_logger.info('Recommended trend request: User %s:%s post number = 0. Use placeholder.' % (user_id, no_watch_next))
            dummy_post_ids = filter_placeholder(user_id, no_watch_next, filter_args)
            # dummy_post_ids = get_ads_discovery(dummy_post_ids)
            return create_response(status=400, content=dummy_post_ids)
        
        # else:
        #     try:
        #         # Add ads to discovery trending
        #         # post_ids = get_ads_discovery(post_ids)
        #         pass
        #     except Exception as e:
        #         deviation_logger.info(f"Failed to load ads post to Search result: {e} \n")

        logger.info('Recommend trend request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        return create_response(status=200, content=post_ids)
    except Exception as e:
        err_logger.info('Recommendation trend critical error: %s' % str(e), exc_info=True)
        return create_response(status=200, content=static_placeholder())


@app.post('/watch_next_foryou' )
@short_api_log
async def personalize_recommend(input_map: schemas.WatchnextSchema, request:Request ): 
    user_id = None
    no_watch_next = None
    filter_args = {
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }

    try:
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
        
        if not CONST_MAP.light_mode:
            if user_id == 130381: # Acc thaomy, of team curator
                post_ids = matching_user_with_content(user_id, no_watch_next, 'manual_curating', filter_args)         
            
            elif user_id == -1:
                final_results = matching_user_with_content_redis(discovery_type='personalize')
                if input_map['filter']['sex']:
                    if input_map['filter']['sex'] == [1]:
                        post_ids = final_results[0]
                    elif input_map['filter']['sex'] == [1, 2]:
                        post_ids = final_results[0] + final_results[1]
                    else:
                        post_ids = final_results[1]
                else:
                    post_ids = final_results[0] + final_results[1]
                random.shuffle(post_ids)
            
            else:
                post_ids = matching_user_with_content(user_id, no_watch_next, 'personalize', filter_args)

        else:
            final_results = matching_user_with_content_redis(discovery_type='personalize')
            if input_map['filter']['sex']:
                if input_map['filter']['sex'] == [1]:
                    post_ids = final_results[0]
                elif input_map['filter']['sex'] == [1, 2]:
                    post_ids = final_results[0] + final_results[1]
                else:
                    post_ids = final_results[1]
            else:
                post_ids = final_results[0] + final_results[1]
            random.shuffle(post_ids)

        if len(post_ids) <= 0:
            deviation_logger.info('Recommended personalize request: User %s:%s post number = 0. Use placeholder. \n' % (user_id, no_watch_next))
            # Add ads to dummy discovery for you
            dummy_post_ids = filter_placeholder(user_id, no_watch_next, filter_args)
            # dummy_post_ids = get_ads_discovery(dummy_post_ids)
            
            return create_response(status=200, content=dummy_post_ids)
        
        # else:
        #     try:
        #         # Add ads to discovery for you
        #         # post_ids = get_ads_discovery(post_ids)
        #         pass
        #     except Exception as e:
        #         deviation_logger.info(f"Failed to load ads post to Search result: {e} \n")

        logger.info('Recommend personalize request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        return create_response(status=200, content=post_ids)
    except Exception as e:
        err_logger.info('Recommendation personalize critical error: %s \n' % str(e), exc_info=True)
        return create_response(status=500, content=static_placeholder())


@app.post('/watch_next_dummy')
@short_api_log
async def placeholder_recommend(input_map: schemas.WatchnextSchema, request:Request):
    filter_args = {
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }
    try:
        input_map = jsonable_encoder(input_map)
        logger.info('%s: Recommend trend request: start: %s' % (request.client.host, str(input_map)))
        user_id = input_map['user_id']
        no_watch_next = input_map['no_watch_next']
        
        if 'filter' in input_map:
            if 'catergory' in input_map['filter']:
                filter_args['category'] = input_map['filter']['catergory']
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
        
        if not CONST_MAP.light_mode:
            post_ids = filter_placeholder(user_id, no_watch_next, filter_args)
        
        else:
            final_results = matching_user_with_content_redis(discovery_type='dummy')
            if input_map['filter']['sex']:
                if input_map['filter']['sex'] == [1]:
                    post_ids = final_results[0]               
                elif input_map['filter']['sex'] == [1, 2]:
                    post_ids = final_results[0] + final_results[1]
                else:
                    post_ids = final_results[1]
            else:
                post_ids = final_results[0] + final_results[1]
            random.shuffle(post_ids)
        
        if len(post_ids) <= 0:
            deviation_logger.info('Recommended placeholder request: User %s:%s post number = 0. Use unfiltered placeholder.' % (user_id, no_watch_next))
            return create_response(status=200, content=static_placeholder())
        logger.info('Recommend placeholder request: finish %s: get result %s' % (str(input_map), str(post_ids)))
        
        return create_response(status=200, content=post_ids)
    except Exception as e:
        err_logger.info('Recommendation placeholder critical error: %s' % str(e), exc_info=True)
        return create_response(status=500,content=static_placeholder())
