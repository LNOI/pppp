import os
import sys
import pathlib
import signal
import logging
import logging.config

import uvicorn

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi import File, Form, Header
from pydantic import BaseModel

from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.const import config_map, resource_map
from src.api_endpoint import add_api


def sigterm_handler(signalNumber, frame):
    raise KeyboardInterrupt


os.chdir(pathlib.Path(__file__).parent)


signal.signal(signal.SIGTERM, sigterm_handler)
if not os.path.isdir('log'):
    os.mkdir('log')
    

if __name__ == '__main__':
    print(f"SYS arg: {sys.argv}")
    if len(sys.argv) >= 2:
        CONFIG_SET = sys.argv[1]

    config_map.load_all_config(CONFIG_SET, CONFIG_MAP)

    # if 'fastapi_app' in CONFIG_MAP['resource'].keys():
    #     CONFIG_MAP['resource'].pop('flask_app')

    resource_map.load_all_resource(CONFIG_MAP, RESOURCE_MAP)

    logging.config.dictConfig(CONFIG_MAP['logging'])
    logger = logging.getLogger('utils_logger')

    app = RESOURCE_MAP['fastapi_app']

    add_api.add_api()

    print(f"Run app at : {CONFIG_MAP['app']['host']}")
    

    if CONFIG_SET == "dev" or CONFIG_SET == "test":
        # host = 'localhost' if run local else 'api_gateway'
        uvicorn.run(app, port=CONFIG_MAP["app"]["port"], host=CONFIG_MAP["app"]["host"], debug=True)
        
