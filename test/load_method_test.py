import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

import unittest
from flask import Flask
from src.const.global_map import CONFIG_SET, CONFIG_MAP
from src.const.config_map import load_all_config
from src.utils.model import *
from src.utils.load_method.load_utils import load_single_resource
from src.utils.load_method.flask_resource import flask_app

import typing

class Test_flask_app(unittest.TestCase):
    def test_OK(self):
        app = flask_app()
        self.assertIsInstance(app, Flask)

if __name__=='__main__':
    unittest.main()