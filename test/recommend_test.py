import os
import sys
import pathlib
os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

import numpy as np
from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const import const_map as CONST_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_single_resource
CONFIG_SET = 'test'
load_all_config(CONFIG_SET, CONFIG_MAP)
load_single_resource('db_engine', RESOURCE_MAP)
load_single_resource('redis_conn', RESOURCE_MAP)

import unittest
from type_test import function_type_test, result_type_test

from src.recommendation.utils.recsys_scoring import _distance_score, _score, get_post_scores
from src.common.random_shuffle import result_prob_random_change
from src.recommendation.source.shop_source import shop_post_raw
from src.utils.exception import NoneInputError
import random
import time
class TestHelper(unittest.TestCase):
    def test_result_prob_random_change(self):
        input_map = {2000:0.01, 2001:0.02}
        res = result_prob_random_change(input_map, 2)
        self.assertTrue(result_type_test(result_prob_random_change, res))

    def test_type(self):
        self.assertTrue(function_type_test(_distance_score))
        self.assertTrue(function_type_test(_score))
        self.assertTrue(function_type_test(get_post_scores))
        
    def test_score(self):
        vector_list_target = np.random.rand(1,128)
        vector_list_like = [np.random.rand(1,128) for i in range(10)]
        vector_list_dislike = [np.random.rand(1,128) for i in range(10)]
        vector_list_like_time = [random.randint(CONST_MAP.history_min_like_time, CONST_MAP.history_max_like_time) for i in range(10)]
        vector_list_dislike_time = [random.randint(CONST_MAP.history_min_dislike_time, CONST_MAP.history_max_dislike_time) for i in range(10)]
        res = _score(vector_list_like, vector_list_dislike, vector_list_like_time, vector_list_dislike_time, vector_list_target)
        res_empty_like = _score([], vector_list_dislike, [], vector_list_dislike_time, vector_list_target)
        res_empty_dislike = _score(vector_list_like, [], vector_list_like_time, [], vector_list_target)
        self.assertTrue(result_type_test(_score, res))

    def test_get_candidate_scores(self):
        vector_list_target = enumerate([np.random.rand(1,128) for i in range(10)])
        vector_list_like = [np.random.rand(1,128) for i in range(10)]
        vector_list_dislike = [np.random.rand(1,128) for i in range(10)]
        vector_list_like_time = [random.randint(0,20) for i in range(10)]
        vector_list_dislike_time = [random.randint(0,20) for i in range(10)]

        res = get_post_scores(vector_list_target, vector_list_like, vector_list_dislike)
        self.assertEqual(set(res.keys()), set(range(10)))

from src.recommendation.new_watch_next import create_source_post, transform_input_param, all_source_addition, clean_up
from src.utils.redis_utils import get_post
class TestWatchNext(unittest.TestCase):
    def test_create_source_number(self):
        user_id = [i for i in RESOURCE_MAP['db_engine'].execute('select id from account_user limit 1')][0][0]
        res = transform_input_param(user_id, 10, 'trending', [])
        self.assertTrue(result_type_test(transform_input_param, res))

    def test_create_source_post(self):
        res = create_source_post(['popular', 'featured'], 3, 'trending', {'user_id':3,'price':[0,1000000]})
        self.assertTrue(result_type_test(create_source_post, res))

    def test_all_source_addition(self):
        source_order = ['popular', 'featured']
        source_number = [5,5]
        user_id = 3
        request_type = 'trending'
        filter_args = {
            'user_id':3,
            'price':[0,1000000]
        }
        source_post = create_source_post(source_order, user_id, request_type, filter_args)
        self.assertTrue(result_type_test(create_source_post, source_post))
        res = transform_input_param(source_order, user_id, request_type)
        _, source_number = res
        self.assertTrue(result_type_test(transform_input_param, res))
        result = all_source_addition(source_order, source_post, source_number, 10, user_id)
        self.assertTrue(result_type_test(all_source_addition, result))
        self.assertGreater(len(result), 0)

    def test_clean_up(self):
        result = [1,2,3,4,5,6,7]
        user_id = 3
        number_of_recommend = 5
        res = clean_up(result, user_id, number_of_recommend)
        self.assertTrue(result_type_test(clean_up, res))
        self.assertEqual(len(res), number_of_recommend)
        viewed_ids = [int(i) for i in get_post('uid:recommended:%s' % user_id)]
        for pid in [1,2,3,4,5]:
            self.assertIn(pid, viewed_ids)

from src.recommendation.noti_recommend import trend_content_for_notification, personalize_content_for_notification
class TestNotiRecommend(unittest.TestCase):
    def test_trend_content(self):
        pid = trend_content_for_notification()
        self.assertTrue(result_type_test(trend_content_for_notification, pid))

    def test_personalize_trend(self):
        pid = personalize_content_for_notification(3)
        self.assertTrue(result_type_test(personalize_content_for_notification, pid))

if __name__=='__main__':
    unittest.main()