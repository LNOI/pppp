import os
import sys
import pathlib

os.chdir(pathlib.Path(__file__).absolute().parent.parent)
sys.path.insert(0, str(pathlib.Path(os.getcwd()).absolute()))

import unittest
import requests

from src.const.global_map import CONFIG_SET, CONFIG_MAP, RESOURCE_MAP
from src.const.config_map import load_all_config
from src.const.resource_map import load_single_resource
import time
from src.chat_suggestion.seller_suggestion import seller_suggestion


from src.utils.basemodel.solrsearch_schemas import SolrSearchSchema
from src.utils.basemodel.keyword_schemas import KeywordSuggestionItem

from  pydantic import BaseModel,PydanticValueError,validator
from typing import Optional, Union, List, Any
from fastapi import status
from fastapi.responses import JSONResponse, Response



host = 'localhost'
port = 8671
CONFIG_SET = 'test'
if len(sys.argv) > 1:
    CONFIG_SET = str(sys.argv[1])
load_all_config(CONFIG_SET, CONFIG_MAP)
load_single_resource('db_engine', RESOURCE_MAP)
load_single_resource('redis_conn', RESOURCE_MAP)

def send_request(endpoint:str, json_body:dict, testcase:unittest.TestCase) -> Response:
    url = 'http://{}:{}/{}'.format(host, port, endpoint)
    res = requests.post(url, json = json_body)
    basic_request_assert(res, testcase)
    return res

def basic_request_assert(res:Response, testcase:unittest.TestCase):
    if res.status_code != 200:
        print('-------------------------------------')
        print(res.text)
        print('+++++++++++++++++++++++++++++++++++++')
    testcase.assertEqual(res.status_code, 200)

class KeywordItemSchema(BaseModel):
    keyword :str
    image_url :str

class HashtagItemSchema(BaseModel):
    hashtag : str
    total_post : int
    post_id : List[int]
    subtitle : str

class PostListSchema(BaseModel):
    items : list[int]

class MallItemSchema(BaseModel):
    user_id : int
    thumbnail_post_ids : list[int]
    post_ids : list[int]

class CarouselPostSchema(BaseModel):
    sponsor_ids : list[int]
    post_ids : list[int]

class CarouselShopSchema(BaseModel):
    sponsor_ids : List[int]
    shop_ids : List[int]

class CarouselSchema(BaseModel):
    post : CarouselPostSchema
    shop : Optional[CarouselShopSchema]

class PromotedShopItemSchema(BaseModel):
    shop_id : int
    shop_post_ids : list[int]                                                                                                                                                                                                                                                                                                                                                                 

class CollectionSchema(BaseModel):
    post_ids : list[int]
    
   
class  LeaderboardDataItemSchema(BaseModel):
    type : str
    title: str
    content: str
    ids: list[int]
    rank_change : list[int]
    score : list[float]
    user : Any
    
    
class LeaderboardDataSchema(BaseModel):
    Tuần : LeaderboardDataItemSchema
    Tháng : LeaderboardDataItemSchema
    

class LeaderboardSchema   
        
    
class LeaderboardDataItemSchema(Schema):
    type = fields.String(require=True, validate=[OneOf(['post', 'user_account'])])
    title = fields.String(require=True, validate=[OneOf(['Bài đăng', 'Shop', 'Pass đồ Rinh xu'])])
    content = fields.String(require=True)
    ids = fields.List(fields.Integer(strict=True, require=True, validate=[Range(min=1)]))
    rank_change = fields.List(fields.Integer(strict=True, require=True))
    score = fields.List(fields.Float(strict=True, required=True))
    user = fields.Raw()

class LeaderboardDataSchema(Schema):
    Tuần = fields.Nested(LeaderboardDataItemSchema)
    Tháng = fields.Nested(LeaderboardDataItemSchema)

class LeaderboardSchema(Schema):
    period = fields.List(fields.String(require=True), require=True)
    title = fields.List(fields.String(require=True), require=True)
    data = fields.List(fields.Nested(LeaderboardDataSchema))



class TestPutToQueue(unittest.TestCase):
    def test_post_encode_OK(self):
        encode_post_ids = [i[0] for i in RESOURCE_MAP['db_engine'].execute('select id from post order by random() limit 1')]
        encode_post_ids = encode_post_ids[:1]
        print('Integration test: Post encode: Post %s' % encode_post_ids)

        send_request('post_encoding', encode_post_ids, self)
        rc = RESOURCE_MAP['redis_conn']
        self.assertIn(encode_post_ids[0], set([int(i) for i in rc.smembers('set_encode_queue:resize')]))
        self.assertIn(encode_post_ids[0], set([int(i) for i in rc.smembers('set_encode_queue:similarity_5')]))

    def test_user_update_OK(self):
        user_ids = [int(i[0]) for i in RESOURCE_MAP['db_engine'].execute('select id from account_user order by random() limit 1')]
        update_user_id = user_ids[0]
        print('Integration test: User update: User %s' % update_user_id)

        send_request('user_update', {'user_id':update_user_id}, self)
        rc = RESOURCE_MAP['redis_conn']
        self.assertIn(update_user_id, set([int(i) for i in rc.smembers('set_queue:user_update')]))

class TestHomeContent(unittest.TestCase):
    def test_home_content_OK(self):
        from src.home_content.banner_component import BannerComponentSchema
        from src.home_content.event_component import EventComponentSchema
        from src.home_content.hashtag_component import HashtagComponentSchema
        from src.home_content.search_component import SearchComponentSchema
        from src.home_content.shop_component import ShopComponentSchema
        from src.home_content.tab_frame_component import TabframeComponentSchema
        from src.home_content.utility_carousel import UtilityComponentSchema
        
        # url = 'http://{}:{}/{}'.format(host, port, 'home_cache_refresh')
        # print(url)
        # # res = requests.get(url)
        # body={"user_id":154824}
        # res = requests.request("GET", url, json=body)
        # basic_request_assert(res, self)

        body = {'user_id': 154824}
        res = send_request('home', body, self)
        body = {'user_id': 3}
        s = time.time()
        # fast_res = send_request('fast_home', body, self)
        # fast_home_time = time.time() - s
        # self.assertGreater(4, fast_home_time)
        
        json_result = res.json()
        # self.assertEqual(json_result, fast_json_result)
        for json_comp in json_result:
            if json_comp['type'] == 'event_banner':
                EventComponentSchema().load(json_comp)
            if json_comp['type'] == 'utility_carousel':
                UtilityComponentSchema().load(json_comp)
            if json_comp['type'] == 'banner_component':
                BannerComponentSchema().load(json_comp)
            if json_comp['type'] == 'tab_frame_component':
                TabframeComponentSchema().load(json_comp)
            if json_comp['type'] == 'shop_component':
                ShopComponentSchema().load(json_comp)
            if json_comp['type'] == 'hashtag_component':
                HashtagComponentSchema().load(json_comp)

class TestUtils(unittest.TestCase):
    def test_recommend_OK(self):
        print('test recommend preparation')
        s = time.time()
        trend_recommend_endpoint = 'watch_next_trending'
        personalize_recommend_endpoint = 'watch_next_foryou'
        placeholder_recommend_endpoint = 'watch_next_dummy'
        user_id = [i for i in RESOURCE_MAP['db_engine'].execute('select id from account_user order by random() limit 1')][0][0]
        print('recommend preparation end: %s' % (time.time() - s))
        print('Integration test: Watch next: User %s' % user_id)
        number_of_recommend_post = 5
        body = {
                'user_id':user_id,
                'no_watch_next':number_of_recommend_post,
                'filter':{
                    'price':[0,100],
                    'category':[1,3,4,6]
                }
                
            }
        dashboard_ids = []#dashboard_creation(user_id)
        def watchnext_test_and_assert(endpoint, avoid_duplicate=False):
            total_result = set()
            for _ in range(5):
                print('Test endpoint: %s' % endpoint)
                res = send_request(endpoint, body, self)
                json_result = res.json()
                
                PostListSchema(items=json_result)
                PostListSchema(items=json_result)
                self.assertGreaterEqual(len(json_result), 1)
                if avoid_duplicate:
                    # Check duplicate result in consecutive request
                    real_result = [i for i in json_result if i not in dashboard_ids]
                    print(real_result)
                    self.assertEqual(len(total_result & set(real_result)), 0)
                    total_result = total_result | set(real_result)

        print('start test trending')
        watchnext_test_and_assert(trend_recommend_endpoint)
        
        print('start test personalize')
        watchnext_test_and_assert(personalize_recommend_endpoint)
        
        print('start test placeholder')
        s = time.time()
        watchnext_test_and_assert(placeholder_recommend_endpoint, avoid_duplicate=False)
        placeholder_total_time = time.time() - s
        print(f"Discovery placeholder time : {placeholder_total_time}")
        self.assertLessEqual(10, placeholder_total_time)
        

    def test_get_similar_post_OK(self):
        similar_post_endpoints = ['similar_post']
        post_ids = [i[0] for i in RESOURCE_MAP['db_engine'].execute('select id from post p where p.is_deleted=false order by random() limit 5')]
        for similar_post_endpoint in similar_post_endpoints:
            total_res = []
            for i in range(len(post_ids)):
                print('Integration test: Similar query: Post %s' % post_ids[i])
                body = {
                    'post_id':post_ids[i],
                    'number_of_post':5
                }
                res = send_request(similar_post_endpoint, body, self)
                json_body = res.json()
                PostListSchema().load({'items':json_body})
                total_res += json_body
            # self.assertGreater(len(total_res), 0)

    def test_personalize_noti_OK(self):
        endpoints = ['personalize_noti']
        user_id = 513
        print('Integration test: Personalize notification: User %s' % user_id)
        body = {
            'user_id':user_id
        }
        for endpoint in endpoints:
            url = 'http://{}:{}/{}'.format(host, port, endpoint)
            res = requests.post(url, json=body)
            if res.status_code == 200:
                pass
            else:
                self.assertEqual(res.status_code, 500)
                self.assertEqual(res.text, 'No satisfy recsys post to recommend personalize content.')

class TestPopularKeywordHashtag(unittest.TestCase):
    def test_popular_keyword_OK(self):
        number_of_keyword = 3
        body = {'number_of_keyword': number_of_keyword}
        res = send_request('popular_keyword', body, self)
        json_result = res.json()
        for obj_result in json_result:
            KeywordItemSchema.parse_obj(obj_result)
        self.assertEqual(len(json_result), number_of_keyword)

    # def test_popular_hashtag_OK(self):
    #     number_of_hashtag = 3
    #     body = {'number_of_hashtag': number_of_hashtag}
    #     res = send_request('popular_hashtag_v2', body, self)
    #     json_result = res.json()
    #     HashtagItemSchema(many=True).load(res.json())
    #     self.assertEqual(len(json_result), number_of_hashtag)

    def test_hashtag_suggestion_OK(self):
        from src.utils.basemodel.hashtag_schemas import HashtagSuggestionItemSchema
        number_of_hashtag = 3
        body = {'user_id':3, 'number_of_hashtag': number_of_hashtag}
        res = send_request('hashtag_suggestion', body, self)
        json_result = res.json()
        
        HashtagSuggestionItemSchema(many=True).load(res.json())
        self.assertEqual(len(json_result), number_of_hashtag)

    def test_hashtag_suggestion_v2_OK(self):
        from src.utils.basemodel.hashtag_schemas import HashtagSuggestionSourceSchema
        number_of_hashtag = 3
        body = {'user_id':3, 'number_of_hashtag': number_of_hashtag}
        res = send_request('hashtag_suggestion_v2', body, self)
        for result in res.json():
            HashtagSuggestionSourceSchema.parse_obj(result)

    def test_keyword_search_OK(self):
        body = {'user_id':513, 'keyword':'thanh lý'}
        res = send_request('keyword_search', body, self)
        for result in res.json():
            SolrSearchSchema.parse_obj(result)

    def test_keyword_suggestion(self):
        number_of_keyword=40
        body = {'user_id':513, 'number_of_keyword':number_of_keyword}
        res = send_request('keyword_suggestion', body, self)
        for result in res.json():  
            KeywordSuggestionItem.parse_obj(result)
        
        json_result = res.json()
        self.assertGreaterEqual(sum([len(i['keywords']) for i in json_result]), number_of_keyword)

class TestMiscApi(unittest.TestCase):
    def test_chat_suggestion_OK(self):
        data = [tuple(i) for i in RESOURCE_MAP['db_engine'].execute('select id, user_id from post p order by random() limit 1')]
        seller_post_id, seller_id = data[0]
        seller_body = {
            'user_id':seller_id,
            'post_id':seller_post_id
        }
        res = send_request('chat_suggestion', seller_body, self)
        self.assertEqual(res.json(), seller_suggestion())
        
        buyer_body = {
            'user_id':seller_id+1,
            'post_id':seller_post_id
        }
        res = send_request('chat_suggestion', buyer_body, self)
        self.assertEqual(list, type(res.json()))
        self.assertEqual(dict, type(res.json()[0]))
        self.assertNotEqual(res.json(), seller_suggestion())
    def test_post_suggest_for_user(self):
        body = {'user_id':3, 'post_id':1}
        res = send_request('post_suggest_for_user', body, self)
        # self.assertGreater(len(res.json()), 0)

class TestCarousel(unittest.TestCase):
    def test_leaderboard_path_OK(self):
        from src.leaderboard.get_leaderboard_post import LeaderboardSchema
        body = {
            "user_id":513
        }
        res = send_request('leaderboard', body, self)
        LeaderboardSchema().load(res.json())
        body = {
            "user_id":5131
        }
        res = send_request('leaderboard', body, self)
        LeaderboardSchema().load(res.json())

class TestPrivateApi(unittest.TestCase):
    def test_OK(self):
        body_user = {'user_id':513}
        res = send_request('user_history', body_user, self)
        self.assertIn('liked_posts', res.json())
        self.assertIn('disliked_posts', res.json())
        print(res.json())

        body_user = {'user_id':513}
        res = send_request('user_vector', body_user, self)
        self.assertIn('user_vector', res.json())
        print(res.json())

        body_user = {'post_id':2000}
        res = send_request('post_vector', body_user, self)
        self.assertIn('post_vector', res.json())
        print(res.json())

        body_user = {'user_id':513, 'post_id':2000}
        res = send_request('user_post_scoring', body_user, self)
        self.assertIn('score', res.json())
        print(res.json())

if __name__=='__main__':
    if len(sys.argv) > 1:
        sys.argv.pop()
    unittest.main(verbosity=2)