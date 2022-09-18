from src.const.global_map import RESOURCE_MAP
from typing import List, Any, Optional
from src.utils.exception import RedisError
from src.utils.decorator import add_exception
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')
error_logger = logging.getLogger('error_logger')

def redis_prefix_key_search(prefix:str) -> List[str]:
    res = RESOURCE_MAP['redis_conn'].keys(prefix+'*')
    return [i.decode('utf-8') for i in res]

def redis_mget(ids:List[str], step_size=5000) -> list[Optional[bytes]]:
    if len(ids) == 0:
        return []
    start_index = 0
    res = []
    while start_index < len(ids):
        res += RESOURCE_MAP['redis_conn'].mget(*ids[start_index:(start_index+step_size)])
        start_index += step_size
    return res

def insert_to_list_key(key:str, values:List[Any], expire:int, trim_limit:Optional[int]=None, expire_update:bool=True) -> None:
    work_logger.info('Redis key %s: insert values %s with expire sec %s' % (key, values, expire))
    if len(values) > 0:
        with RedisPipeline(RESOURCE_MAP['redis_conn'], transaction=False) as pipe:
            pipe.rpush(key, *values)
            if trim_limit is not None:
                pipe.ltrim(key, -trim_limit, -1)
            if expire > 0 and expire_update:
                pipe.expire(key, expire)

def insert_to_set_key(key:str, value:int, expire:int) -> None:
    if value != None:
        RESOURCE_MAP['redis_conn'].sadd(key, value)
        if expire > 0:
            RESOURCE_MAP['redis_conn'].expire(key, expire)

@add_exception(RedisError, Exception)
def get_post(key:str) -> list[int]:
    return [int(i) for i in RESOURCE_MAP['redis_conn'].lrange(key, 0, -1)]

def insert_and_trim(id_key:str, id_list:list[int], time_key:str, time_list:list[float], expire_secs=86400, trim_limit=50) -> None:
    if len(id_list) < 1:
        with RedisPipeline(RESOURCE_MAP['redis_conn']) as pipe:
            pipe.expire(id_key, expire_secs)
            pipe.expire(time_key, expire_secs)
        return
    else:
        old_id = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange(id_key, 0, -1)]
        old_time = [float(i) for i in RESOURCE_MAP['redis_conn'].lrange(time_key, 0, -1)]
        filtered_old_history = [item for item in zip(old_id, old_time) if item[0] not in id_list]

        new_history = list(zip(id_list, time_list))
        total_history = filtered_old_history + new_history
        trimed_total_history = total_history[-trim_limit:]
        trimed_post_id, trimed_post_time = zip(*trimed_total_history)

        with RedisPipeline(RESOURCE_MAP['redis_conn']) as pipe:
            pipe.delete(id_key)
            pipe.rpush(id_key, *trimed_post_id)
            pipe.ltrim(id_key, -trim_limit, -1)
            pipe.delete(time_key)
            pipe.rpush(time_key, *trimed_post_time)
            pipe.ltrim(time_key, -trim_limit, -1)
            pipe.expire(id_key, expire_secs)
            pipe.expire(time_key, expire_secs)
        return

class RedisPipeline():
    def __init__(self, redis_conn, transaction=True):
        self.redis_conn = redis_conn
        self.transaction = transaction
    def __enter__(self):
        self.pipe = self.redis_conn.pipeline(transaction=self.transaction)
        return self.pipe
    def __exit__(self, error_type, error, traceback):
        self.pipe.execute()        
        if error is not None:
            error_logger.error(error, exc_info=True)
            
@add_exception(RedisError, Exception)
def get_viewed_post(user_id:int) -> List[int]:
    liked_post_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:like:%s' % user_id, -300, -1) if int(i) > 0]
    disliked_post_ids = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:dislike:%s' % user_id, -300, -1) if int(i) > 0]
    previous_recommend_post_ids = list(set([int(i) for i in RESOURCE_MAP['redis_conn'].lrange('uid:recommended:%s' % user_id, -1000, -1)  if int(i) > 0]))
    work_logger.info('User: %s. Like history: %s' % (user_id, liked_post_ids))
    work_logger.info('User: %s. Dislike history: %s' % (user_id, disliked_post_ids))
    work_logger.info('User: %s. Recommended history: %s' % (user_id, previous_recommend_post_ids))
    total_post_ids = liked_post_ids + disliked_post_ids + previous_recommend_post_ids
    return total_post_ids
