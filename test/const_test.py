import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

import unittest
from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_all_resource, load_single_resource
from src.utils.model import *
import typing
class Test_load_all_config(unittest.TestCase):
    def test_OK(self):
        print('test load all config')
        CONFIG_MAP = {}
        load_all_config(CONFIG_SET, CONFIG_MAP)
        self.assertCountEqual(CONFIG_MAP.keys(), ['app', 'resource','logging'])
        for config_name in ['app', 'resource','logging']:
            self.assertIsInstance(CONFIG_MAP[config_name], dict)

class Test_load_all_resource(unittest.TestCase):
    def test_OK(self):
        print('test load all resource')
        load_all_config(CONFIG_SET, CONFIG_MAP)
        RESOURCE_MAP = {}
        load_all_resource(CONFIG_MAP, RESOURCE_MAP)
        self.assertCountEqual(CONFIG_MAP['resource'].keys(), RESOURCE_MAP.keys())
        
class Test_load_single_resource(unittest.TestCase):
    def test_OK(self):
        print('test load single resource')
        load_all_config(CONFIG_SET, CONFIG_MAP)
        RESOURCE_MAP = {}
        loaded_resource = set()
        for key in CONFIG_MAP['resource']:
            load_single_resource(key, RESOURCE_MAP)
            loaded_resource = loaded_resource | set([key])
            self.assertEqual(loaded_resource, set(RESOURCE_MAP.keys()))

    def test_not_exist(self):
        print('test load non exist resource')
        load_all_config(CONFIG_SET, CONFIG_MAP)
        RESOURCE_MAP = {}
        with self.assertRaises(KeyError) as context:
            load_single_resource('not_exist', RESOURCE_MAP)

if __name__=='__main__':
    unittest.main()