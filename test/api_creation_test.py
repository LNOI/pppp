import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

import unittest
from collections import namedtuple

from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_single_resource
from src.api_endpoint.add_api import add_api

CONFIG_SET = 'test'
load_all_config(CONFIG_SET, CONFIG_MAP)
load_single_resource('flask_app', RESOURCE_MAP)
load_single_resource('redis_conn', RESOURCE_MAP)
Url_rule = namedtuple('UrlRule', ['rule', 'methods'])

class Test_add_api(unittest.TestCase):
    def test_OK(self):
        add_api()
        endpoint_rules_map = {item.endpoint:Url_rule(item.rule, item.methods) for item in RESOURCE_MAP['flask_app'].url_map.iter_rules()}
        for endpoint in CONFIG_MAP['app']:
            if endpoint not in ['host', 'port','numthread']:
                self.assertIn(endpoint, endpoint_rules_map)
                self.assertEqual(CONFIG_MAP['app'][endpoint]['rule'], endpoint_rules_map[endpoint].rule)
                self.assertTrue(endpoint_rules_map[endpoint].methods.issuperset(CONFIG_MAP['app'][endpoint]['methods']))

if __name__=='__main__':
    unittest.main()