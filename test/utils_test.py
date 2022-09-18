import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

if not os.path.isdir('../file_cache'):
    os.mkdir('../file_cache')

from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_single_resource
CONFIG_SET = 'test'
load_all_config(CONFIG_SET, CONFIG_MAP)
load_single_resource('redis_conn', RESOURCE_MAP)

from type_test import function_type_test, result_type_test
import unittest
from unittest.mock import patch

import numpy as np

load_single_resource('redis_conn', RESOURCE_MAP)
from src.utils.redis_utils import get_post, insert_to_list_key, insert_and_trim
class TestRedisUtils(unittest.TestCase):
    def test_insert_and_trim_redis(self):
        history_1 = [0, 1, 2, 3, 4, 5, 6, 7]
        time_1 = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        history_2 = [6, 7, 8, 9, 1, 3, 5]
        time_2 = [6.0, 7.0, 8.0, 9.0, 1.0, 3.0, 5.0]

        expected = [2, 4, 6, 7, 8, 9, 1, 3, 5]
        expected_time = [2.0, 4.0, 6.0, 7.0, 8.0, 9.0, 1.0, 3.0, 5.0]
        RESOURCE_MAP['redis_conn'].delete('test:insert_trim_id')
        RESOURCE_MAP['redis_conn'].delete('test:insert_trim_time')
        insert_and_trim('test:insert_trim_id', history_1, 'test:insert_trim_time', time_1, trim_limit=9)
        insert_and_trim('test:insert_trim_id', history_2, 'test:insert_trim_time', time_2, trim_limit=9)
        res = [int(i) for i in RESOURCE_MAP['redis_conn'].lrange('test:insert_trim_id', 0, -1)]
        self.assertEqual(res, expected)
        res = [float(i) for i in RESOURCE_MAP['redis_conn'].lrange('test:insert_trim_time', 0, -1)]
        self.assertEqual(res, expected_time)
       
    def test_insert_to_list_key(self):
        history_1 = [1,2,3,4,5]
        history_2 = [5,6,7,8,1,2,3]
        expected = [5, 5, 6, 7, 8, 1, 2, 3]
        RESOURCE_MAP['redis_conn'].delete('test:insert')
        insert_to_list_key('test:insert', history_1, 100, trim_limit=8)
        insert_to_list_key('test:insert', history_2, 100, trim_limit=8)
        res = [int(i) for i in get_post('test:insert')]
        self.assertEqual(res, expected)

if __name__=='__main__':
    unittest.main()