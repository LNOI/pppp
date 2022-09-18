import logging

from src.const.global_map import RESOURCE_MAP
from src.utils.basemodel.response_schemas import create_response
from typing import NoReturn


logger = logging.getLogger('app_logger')
app = RESOURCE_MAP['fastapi_app']


@app.get('/ping')
def ping():
    return create_response(status=200, content="Healthy server connection.")


# FastAPI already have openapi swagger docs /docs or /redoc
# @app.route(rule='/doc', methods=['GET'])
# def doc() -> Response:
#     return send_from_directory(directory='./', filename='openapi.yaml', mimetype='text/plain')


@app.get('/shutdown')
def shutdown() -> NoReturn:
    logger.info('Receive server shutdown request.')
    raise KeyboardInterrupt
