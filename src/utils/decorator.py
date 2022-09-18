import time
import inspect
import logging
import functools
import random
from fastapi.encoders import jsonable_encoder
from typing import Callable
from fastapi import Request


from marshmallow.exceptions import ValidationError

from src.utils.basemodel.response_schemas import create_response


app_logger = logging.getLogger('app_logger')
logger = logging.getLogger('utils_logger')
time_logger = logging.getLogger('time_logger')

# dummy function
def get_user_gender(user_id):
    return 2

# if anonymous user (no login) then return dummy user
def anonymous_user(user_id):
    if user_id == -1:
        if (get_user_gender(user_id) == 2):
            return 374462 
        else:
            return 374451
    return user_id


def forward_random_uid(request, type: str):
    if type in ['user_id', 'shop_id']:
        request[type] = -1 #random.randint(1, 300000)
        forward_uid = request[type]
        app_logger.info(f"Anonymous request -> Random to user {forward_uid}")
    else:
        forward_uids = [-1 for i in range(len(request[type]))] #[random.randint(1, 300000) for i in range(len(request[type]))]
        request[type] = forward_uids
        app_logger.info(f"Anonymous request -> Random to user {forward_uids}")   


# def json_validate(schema, err_message, placeholder_result=None):
#     def deco(func):
#         @functools.wraps(func)
#         def validation_wrapper(*args, **kwargs):
            
#             request=kwargs['request']._body.decode()
#             print(request)
#             try:
#                 schema.load(request)
#             except Exception as e:
#                 if 'user_id' in request and request["user_id"] < 1:
#                     forward_random_uid(request=request, type='user_id')
#                     return func(*args, **kwargs)
#                 elif 'shop_id' in request and request["shop_id"] < 1:
#                     forward_random_uid(request=request, type='shop_id')
#                     return func(*args, **kwargs)
#                 elif 'user_ids' in request and request["user_ids"] < 1:
#                     forward_random_uid(request=request, type='user_ids')
#                     return func(*args, **kwargs)
#                 elif 'shop_ids' in request and request["shop_ids"] < 1:
#                     forward_random_uid(request=request, type='shop_ids')
#                     return func(*args, **kwargs)
#                 else:
#                     app_logger.info(err_message + str(e) + 'Input: %s.' %
#                                     str(request.data) + ' Request IP: %s.' % str(request.remote_addr))
#                 if placeholder_result is None:
                   
#                     return create_response(status=400,content=e.messages)
#                 else: 
#                     return create_response(status=400,content=placeholder_result())
#             return func(*args, **kwargs)
#         return validation_wrapper
#     return deco


# def json_plain_validate(schema, err_message, placeholder_result=None):
#     def deco(func):
#         @functools.wraps(func)
#         def validation_wrapper(*args, **kwargs):
#             try:
#                 schema.load({'items': request})
#             except ValidationError as e:
#                 app_logger.info(err_message + str(e) + 'Input: %s.' %
#                                 str(request.data) + ' Request IP: %s.' % str(request.remote_addr))
#                 if placeholder_result is None:
#                     return jsonify(e.messages), 400
#                 else:
#                     return jsonify(placeholder_result()), 400
#             return func(*args, **kwargs)
#         return validation_wrapper
#     return deco


def add_exception(new_exc: type, catch_exc: type = Exception) -> Callable:
    def add_specific_exception(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except catch_exc as e:
                logger.info('Error in %s' % func.__name__, exc_info=True)
                raise new_exc('Error in %s' % func.__name__) from e
        return wrapper_func
    return add_specific_exception


def log_func_time(func: Callable) -> Callable:
    @functools.wraps(func)
    def timed_func(*args, **kwargs):
        s = time.time()
        result = func(*args, **kwargs)
        # depth = len(inspect.stack()) - 14
        # time_logger.info('-'*depth*2 + '%s: Run in %s sec' % (func.__name__, time.time() - s))
        time_logger.info('%s: Run in %s sec' % (func.__name__, time.time() - s))
        return result
    return timed_func
