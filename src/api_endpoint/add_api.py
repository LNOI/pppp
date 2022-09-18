import sys
import functools
import logging

from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response


logger = logging.getLogger('app_logger')
err_logger = logging.getLogger('error_logger')


def api_log(func: Callable):
    """
        API_log function transform a function for process and logging:
        Input:
        - function (def)
        Output:
        - function result and logging (including its name, status, and data result)
    """
    @functools.wraps(func)
    async def api_log_decorator(*args, **kwargs):
        # input_map = request.json()
        input_map = kwargs['input_map']
        request=kwargs['request']
        # logger.info('%s request: start: %s' % (func.__name__, str(kwargs)))
        logger.info("%s: %s request: start: %s", request.client, func.__name__, str(input_map))
        try:
            response = await func(*args, **kwargs)
            if type(response) == Response:
                logger.info('%s request: finish: %s, %s' % (func.__name__, str(response.status), str(response.content)))
            else:
                logger.info('%s request: finish: %s' % (func.__name__, str(response)))
            return response
        except Exception as e:
            err_logger.error('%s request: error: %s' % (func.__name__, e), exc_info=True)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)
    return api_log_decorator


def short_api_log(func:Callable):
    @functools.wraps(func)
    async def api_log_decorator(*args, **kwargs):
        input_map = kwargs['input_map']
        input_map_copy = {}
        for key in input_map:
            if len(str(key[1])) < 200:
                input_map_copy[key[0]] = key[1]
            else:
                input_map_copy[key] = 'Value too long'
        logger.info('%s request: start: %s' % (func.__name__, str(input_map_copy)))
        try:
            response = await func(*args, **kwargs)
            if type(response) == Response:
                logger.info('%s request: finish: %s, %s' % (func.__name__, str(response.status_code), str(response)))
            else:
                logger.info('%s request: finish: %s' % (func.__name__, str(response)))
            return response
        except Exception as e:
            err_logger.error('%s request: error: %s' % (func.__name__, e), exc_info=True)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)
    return api_log_decorator


def api_log_no_response_content(func: Callable):
    """
        API_log_no_res_content function transform a function for process and logging:
        Input:
        - function (def)
        Output:
        - function result and logging (including its name, and status)
    """
    @functools.wraps(func)
    async def api_log_decorator(*args, **kwargs):
        # input_map = request.json()
        logger.info('%s request: start: %s' % (func.__name__, str(kwargs)))
        try:
            response = await func(*args, **kwargs)
           
            if type(response) == ResponseModel:
                logger.info('%s request: finish: %s.' % (func.__name__, str(response.status_code)))
            else:
                logger.info('%s request: finish.' % func.__name__)
            return response
        except Exception as e:
            err_logger.error('%s request: error: %s' % (func.__name__, e), exc_info=True)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)
    return api_log_decorator


def add_api() -> None:
    if "const_api" not in sys.modules:
        import src.api_endpoint.const_api
    if "sys_api" not in sys.modules:
        import src.api_endpoint.sys_api
    if "application_api" not in sys.modules:
        import src.api_endpoint.application_api
    if "watch_next_api" not in sys.modules:
        import src.api_endpoint.watch_next_api
    if "noti_api" not in sys.modules:
        import src.api_endpoint.noti_api
    if "carousel_api" not in sys.modules:
        import src.api_endpoint.carousel_api
    if "home_content_api" not in sys.modules:
        import src.api_endpoint.home_content_api
    if "vf_api" not in sys.modules:
        import src.api_endpoint.vf_api
    if "discovery_api" not in sys.modules:
        import src.api_endpoint.discovery_api
    