import imp
import logging

from src.const.global_map import RESOURCE_MAP
from src.api_endpoint.add_api import api_log, short_api_log
from src.virtual_fit.virtual_fit import get_all_virtual_fit, get_post_virtual_fit

from fastapi.encoders import jsonable_encoder
from src.utils.basemodel.response_schemas import create_response
from src.utils.basemodel import vf_schemas as schemas

logger = logging.getLogger("app_logger")
err_logger = logging.getLogger("error_logger")


app = RESOURCE_MAP["fastapi_app"]


@app.post("/vfit_discovery")
@short_api_log
async def virtual_fitting_discovery(input_map: schemas.VFDiscoverySchema ):
    user_id = input_map.user_id
    model_id = input_map.model_id

    data = get_all_virtual_fit(uid=user_id, mid=model_id)
    return create_response(status=200, content=data)


@app.post("/vfit_onepost")
@short_api_log
async def virtual_fitting_per_post(input_map: schemas.VFPostSchema):
    user_id = input_map.user_id
    model_id = input_map.model_id
    post_id = input_map.post_id

    data = get_post_virtual_fit(uid=user_id, mid=model_id, pid=post_id)
    if len(data) == 0:
        return create_response(status=400, content="Can't fit model with this item.")
    data2 = get_all_virtual_fit(uid=user_id, mid=model_id)

    return create_response(status=400, content=data+data2)
