import logging
from fastapi import Request

from src.api_endpoint.add_api import short_api_log
from src.const.global_map import RESOURCE_MAP

# from src.utils.basemodel import score_preview_schemas as schemas
from src.utils.basemodel import home_content_schemas as schemas
from src.utils.basemodel.response_schemas import create_response
from src.utils.decorator import anonymous_user

from src.const.global_map import RESOURCE_MAP
from src.home_content.home_content import get_placeholder_content, get_segment_home_content, get_banner_content
from src.home_content.home_content import refresh_home_content, refresh_seeded_home_content



logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')

app = RESOURCE_MAP['fastapi_app']


@app.post('/livestream_banner')
@short_api_log
async def banner_content_api(input_map: schemas.HomeContentInputSchema):
    try:
        user_id = input_map.user_id
        user_id = anonymous_user(user_id)
        if input_map.component_index is None:
            content_map_list, index = get_banner_content(user_id)
        else:
            content_map_list, index = get_banner_content(
                user_id, input_map.component_index)
        logger.info('%s request: cache index: %s' %
                    ('home_content_api', str(index)))
    except Exception as e:
        if e.args[0] != 'Home cache is not exist, load placeholder Home.':
            err_logger.error('%s request: Error: %s. Use placeholder.' % (
                'home_content_api', e), exc_info=True)
        else:
            deviation_logger

        content_map_list, index = get_placeholder_content()

    for i in range(len(content_map_list)):
        if content_map_list[i]['id'] == 'event_event':
            content_map_list = [content_map_list[i]]
            break
        else:
            content_map_list = []

    for i in range(len(content_map_list)):
        content_map_list[i]['index'] = i

    return create_response(status=200, content=content_map_list)


@app.post("/home")
@short_api_log
async def home_content_api(input_map: schemas.HomeContentInputSchema, request: Request):
    try:
        user_id = input_map.user_id
        user_id = anonymous_user(user_id)
    
        if input_map.component_index is None:
            content_map_list, index = get_segment_home_content(user_id)
        else:
            content_map_list, index = get_segment_home_content(
                user_id, input_map.component_index)
        logger.info('%s request: cache index: %s' %
                    ('home_content_api', str(index)))
    except Exception as e:
        if e.args[0] != 'Home cache is not exist, load placeholder Home.':
            err_logger.error('%s request: Error: %s. Use placeholder.' % (
                'home_content_api', e), exc_info=True)
        else:
            deviation_logger

        content_map_list, index = get_placeholder_content()
    return create_response(status=200, content=content_map_list)


@app.post("/fast_home")
@short_api_log
async def fast_home_content_api(input_map: schemas.HomeContentInputSchema):
    try:
        user_id = input_map.user_id
        user_id = anonymous_user(user_id)
        if input_map.component_index is None:
            content_map_list, index = get_segment_home_content(user_id)
        else:
            content_map_list, index = get_segment_home_content(
                user_id, input_map.component_index)
        logger.info('%s request: cache index: %s' %
                    ('home_content_api', str(index)))
    except Exception as e:
        if e.args[0] != 'Home cache is not exist, load placeholder Home.':
            err_logger.error('%s request: Error: %s. Use placeholder.' % (
                'home_content_api', e), exc_info=True)
        else:
            deviation_logger

        content_map_list, index = get_placeholder_content()
    return create_response(status=200, content=content_map_list)


@app.get("/home_cache_refresh")
@short_api_log
async def home_cache_refresh(input_map: schemas.HomeContentInputSchema):
    try:
        user_id = input_map.user_id
        status = refresh_seeded_home_content(user_id)
        # refresh_home_content()
        print("Done Refresh Home Content.")
        return status
    except Exception as e:
        err_logger.error('%s request: Error: %s.' % ('home_cache_refresh', str(e)), exc_info=True)
        return 'Error: %s' % str(e)
