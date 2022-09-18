import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

if not os.path.isdir('../file_cache'):
    os.mkdir('../file_cache')

from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_single_resource
CONFIG_SET = 'test'
load_all_config(CONFIG_SET, CONFIG_MAP)

from type_test import function_type_test, result_type_test
import unittest

load_single_resource('db_engine', RESOURCE_MAP)
load_single_resource('redis_conn', RESOURCE_MAP)
from src.utils.db_utils import execute_raw_query

class TestDBUtils(unittest.TestCase):
    def test_execute_raw_query_OK(self):
        query = 'select 1'
        res = execute_raw_query(query)
        self.assertTrue(result_type_test(execute_raw_query, res))
        self.assertEqual(res[0][0], 1)

if __name__=='__main__':
    unittest.main()