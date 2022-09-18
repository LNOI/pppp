import redis
from src.const.global_map import RESOURCE_MAP
from typing import List, Any, Callable
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')
error_logger = logging.getLogger('error_logger')

import functools
def redis_result_cache(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            keys = key_maker(*args, **kwargs)
            if type(keys) != list:
                raise RuntimeError('Error redis cache key naming %s: type %s' % (str(keys), type(keys)))
            rc = RESOURCE_MAP['redis_conn']
            if not all([rc.exists(key) for key in keys]):
                work_logger.info('Redis cache: add new: %s' % str(keys))
                query_result = func(*args, **kwargs)
                for key, value in zip(keys, query_result):
                    if type(value) in [list, tuple]:
                        if rc.exists(key):
                            value = value
                        else:
                            value = (-1, *value)
                        if len(value) > 0:
                            rc.rpush(key, *value)
                    else:
                        rc.set(key, value)
                    rc.expire(key, expire_secs)
            else:
                work_logger.info('Redis cache: reuse: %s' % str(keys))
            redis_result = []
            for key in keys:
                if rc.type(key) == b'list':
                    value = rc.lrange(key, 1, -1)
                else:
                    value = rc.get(key)
                redis_result.append(value)
            return redis_result
        return cache_query_func
    return result_cache_func

def redis_cache_list(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            key = key_maker(*args, **kwargs)
            if type(key) != str:
                raise RuntimeError('Error redis cache key naming %s: require str, get type %s' % (str(key), type(key)))
            rc = RESOURCE_MAP['redis_conn']
            if not rc.exists(key):
                value = func(*args, **kwargs)
                refresh_cache_list(key, value, rc, expire_secs)
            res = get_cached_list(key, rc)
            if 'return' in func.__annotations__:
                if func.__annotations__['return'] in [List[int], List[float], List[str]]:
                    target_type = func.__annotations__['return'].__args__[0]
                    res = [target_type(i) for i in res]
            return res
        return cache_query_func
    return result_cache_func

def redis_cache_multi_list(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            keys = key_maker(*args, **kwargs)
            if type(keys) != list:
                raise RuntimeError('Error redis cache key naming %s: type %s' % (str(keys), type(keys)))
            rc = RESOURCE_MAP['redis_conn']
            if int(rc.exists(*keys)) != len(keys):
                query_result = func(*args, **kwargs)
                for key, value in zip(keys, query_result):
                    refresh_cache_list(key, value, rc, expire_secs)
            redis_result = []
            try:
                return_type = func.__annotations__['return']
                return_type_list = [arg.__args__[0] for arg in return_type.__args__]
                for key, list_type in zip(keys, return_type_list):
                    redis_result.append([list_type(item) for item in get_cached_list(key, rc)])
            except Exception as e:
                raise SyntaxError('Redis cache multi list decorator require correct return type annotation') from e
            return redis_result
        return cache_query_func
    return result_cache_func

def refresh_cache_list(key:str, value:Any, rc:redis.Redis, expire_secs:int) -> None:
    if not rc.exists(key):
        work_logger.info('Redis cache: add new: %s' % str(key))
        if type(value) in [list, tuple]:
            if rc.exists(key):
                value = value
            else:
                value = (-1, *value)
            if len(value) > 0:
                rc.rpush(key, *value)
        else:
            raise RuntimeError('Error redis cache: key %s only accept collection, not simple value as %s' % (key, value))
        rc.expire(key, expire_secs)
    else:
        work_logger.info('Redis cache: reuse: %s' % str(key))

def get_cached_list(key:str, rc:redis.Redis) -> list[Any]:
    if rc.type(key) == b'list':
        value = rc.lrange(key, 1, -1)
    else:
        deviation_logger.error('Redis key %s should have type list' % key)
        value = [rc.get(key)]
    return value

def redis_cache_str(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            key = key_maker(*args)
            if type(key) != str:
                raise RuntimeError('Error redis cache key naming %s: require str, get type %s' % (str(key), type(key)))
            rc = RESOURCE_MAP['redis_conn']
            if not rc.exists(key):
                work_logger.info('Redis cache: add new: %s' % str(key))
                value = func(*args, **kwargs)
                if type(value) is not str:
                    raise RuntimeError('Error redis cache: key %s only accept string type' % key)
                else:
                    rc.set(key, value)
                rc.expire(key, expire_secs)
            else:
                work_logger.info('Redis cache: reuse: %s' % str(key))
            if rc.type(key) != b'list':
                return rc.get(key).decode('utf-8')
            else:
                deviation_logger.error('Redis key %s should not have type list' % key)
                return rc.lrange(key, 1, -1)[0].decode('utf-8')
        return cache_query_func
    return result_cache_func

def redis_cache_value(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            key = key_maker(*args, **kwargs)
            if type(key) != str:
                raise RuntimeError('Error redis cache key naming %s: require str, get type %s' % (str(key), type(key)))
            rc = RESOURCE_MAP['redis_conn']
            if not rc.exists(key):
                work_logger.info('Redis cache: add new: %s' % str(key))
                value = func(*args, **kwargs)
                if type(value) in [list, tuple]:
                    raise RuntimeError('Error redis cache: key %s only accept simple value, not collection as %s' % (key, value))
                else:
                    rc.set(key, value)
                rc.expire(key, expire_secs)
            else:
                work_logger.info('Redis cache: reuse: %s' % str(key))
            if rc.type(key) != b'list':
                return rc.get(key)
            else:
                deviation_logger.error('Redis key %s should not have type list' % key)
                return rc.lrange(key, 1, -1)[0]
        return cache_query_func
    return result_cache_func

import json
def redis_cache_json(key_maker:Callable, expire_secs:int) -> Callable:
    def result_cache_func(func:Callable) -> Callable:
        @functools.wraps(func)
        def cache_query_func(*args, **kwargs):
            key = key_maker(*args, **kwargs)
            if type(key) != str:
                raise RuntimeError('Error redis cache key naming %s: require str, get type %s' % (str(key), type(key)))
            rc = RESOURCE_MAP['redis_conn']
            if not rc.exists(key):
                work_logger.info('Redis cache: add new: %s' % str(key))
                value = func(*args, **kwargs)
                set_redis_json_value(value, key, expire_secs)
            else:
                work_logger.info('Redis cache: reuse: %s' % str(key))
            if rc.type(key) != b'list':
                redis_serialized_str = rc.get(key).decode('utf-8')
                dict_value = json.loads(redis_serialized_str)
                return dict_value
            else:
                deviation_logger.error('Redis key %s should not have type list' % key)
                redis_serialized_str = str(rc.lrange(key, 1, -1)[0])
                dict_value = json.loads(redis_serialized_str)
                return dict_value
        return cache_query_func
    return result_cache_func

def set_redis_json_value(value, key, expire_secs):
    rc = RESOURCE_MAP['redis_conn']
    try:
        serialized_str = json.dumps(value)
    except Exception as e:
        raise RuntimeError('Error redis cache: key %s: cannot serialize value %s to json: error %s' % (key, value, e))
    if 'segment_home_content' in key:
        print('Key %s: Expire %s' % (key, expire_secs))
        if expire_secs < 3600:
            raise Exception('Catch the bug')
    rc.set(key, serialized_str)
    rc.expire(key, expire_secs)

def get_redis_json_value(key):
    rc = RESOURCE_MAP['redis_conn']
    try:
        redis_serialized_str = rc.get(key).decode('utf-8')
        dict_value = json.loads(redis_serialized_str)
        return dict_value
    except Exception as e:
        deviation_logger.error('Get key %s error: %s' % (key, str(e)), exc_info=True)
        return None