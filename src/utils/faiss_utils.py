import numpy as np
from src.const import const_map as CONST_MAP
from src.utils.exception import FaissIndexError
from src.utils.decorator import add_exception, log_func_time

import requests
from urllib.parse import urljoin

from typing import List
import logging
logger = logging.getLogger('utils_logger')

@add_exception(FaissIndexError, RuntimeError)
def delete_id(post_id:int, index:str) -> None:
    url = urljoin(str(CONST_MAP.faiss_api_endpoint), r'/s_delete')
    body = {
        'post_id':post_id,
        'index_name':index
    }
    res = requests.post(url, json=body)
    if res.status_code != 200:
        raise FaissIndexError('Error faiss when delete %s from %s: %s' % (post_id, index, res.text))

@log_func_time
@add_exception(FaissIndexError, Exception)
def read_index_by_multiple_ids(post_ids:list[int], index:str) -> dict[int, np.ndarray]:
    url = urljoin(str(CONST_MAP.faiss_api_endpoint), r'/s_read_multi')
    body = {
        'post_ids':post_ids,
        'index_name':index
    }
    res = requests.post(url, json=body)
    if res.status_code != 200:
        raise FaissIndexError('Error faiss when read multi post %s from %s: %s' % (post_ids, index, res.text))
    post_vec_map = {int(k):np.array(v).reshape(-1) for k,v in res.json().items()}
    return post_vec_map

def multi_search_index_condition(arrs:list[np.ndarray], k:int, index:str, category:int=-1, threshold:float=1, avoid_ids=None) -> List[int]:
    # if 'style' in index:
    #     return []
    if avoid_ids == None:
        avoid_ids = []
    url = urljoin(str(CONST_MAP.faiss_api_endpoint), r'/s_search_multi_vector_condition')
    body = {
        'vectors':[arr.astype(np.float32).reshape(-1).tolist() for arr in arrs],
        'number_of_post':k,
        'category':category,
        'threshold':threshold,
        'avoid_ids':avoid_ids,
        'index_name':index
    }
    res = requests.post(url, json=body)
    if res.status_code != 200:
        raise FaissIndexError('Error faiss when search nearby from %s: %s' % (index, res.text))
    post_ids = [int(i) for i in res.json()['post_ids']]
    return post_ids


def sim_5_multi_search_index(post_id:int, k:int, threshold:float=1) -> List[int]:
    url = urljoin(str(CONST_MAP.faiss_api_endpoint), r'/s5_search_multi_vector')
    body = {
        'post_id':post_id,
        'number_of_post':k,
        'threshold':threshold
    }
    res = requests.post(url, json=body)
    if res.status_code != 200:
        raise FaissIndexError('Error faiss when sim 5 search nearby: %s' % res.text)
    post_ids = [int(i) for i in res.json()['post_ids']]
    return post_ids
