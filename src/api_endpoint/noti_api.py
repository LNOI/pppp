import logging

from src.const.global_map import RESOURCE_MAP
from src.const.global_map import RESOURCE_MAP
from src.api_endpoint.add_api import api_log, short_api_log
from src.utils.exception import NotificationError
from src.recommendation.noti_recommend import personalize_content_for_notification
from src.recommendation.noti_recommend import following_post_notification, popular_post_notification
from src.utils.basemodel.response_schemas import create_response
from src.utils.basemodel import  noti_schemas as schemas

logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')

app = RESOURCE_MAP['fastapi_app']
    

@app.post('/personalize_noti')
@short_api_log
async def personalize_noti(input_map: schemas.PersonalizeNotiSchema ):
    user_id = input_map.user_id
    try:
        post_id = personalize_content_for_notification(user_id)
        return str(post_id), 200
    except NotificationError as e:
        deviation_logger.error('Personalize noti error: %s' % e, exc_info=True)
        return create_response(status=500, content= str(e))


@app.post('/following_noti')
@short_api_log
async def following_noti(input_map: schemas.FollowingNotiSchema):
    user_ids = input_map.user_ids
    res = following_post_notification(user_ids)
    return create_response(status=200, content=res)

@app.post('/popular_noti')
@short_api_log
async def popular_noti():
    res = popular_post_notification()
    return create_response(status=200, content=res)