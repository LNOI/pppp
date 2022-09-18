import random
import time
import datetime
import unicodedata

from marshmallow import Schema, fields
from marshmallow.validate import URL, OneOf, Range


from src.carousel.common import get_content_post_ids, get_user_thubmnail_post_id
from src.carousel.shop_promotion import get_promoted_shop, get_common_promoted_shop, query_consignment_candidates, get_weekly_shop
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_s3_presign_url
from src.const import const_map as CONST_MAP
from src.home_content.utils import register_home_component
from src.utils.marshmallow_utils import NullableURL


class BaseShopComponent:
    def __init__(self, **kwargs) -> None:
        self.sub_id = None

        serialized_json_data = kwargs.get('serialized_json_data', None)
        if serialized_json_data is None:
            self.refresh_new_data(**kwargs)
        else:
            self.shop_ids = serialized_json_data['shop_ids']
            self.header = serialized_json_data['header']
            self.titles = serialized_json_data['titles']
            self.avatar_urls = serialized_json_data['avatar_urls']
            self.post_idss = serialized_json_data['post_idss']
            self.thumbnailss = serialized_json_data['thumbnail_post_idss']
        
    def refresh_new_data(self, **kwargs):
        raise NotImplementedError('Should not use base shop class')

    def refresh_detail_from_shop_ids(self):
        shop_infos = get_shop_info(self.shop_ids)
        self.titles = [shop_infos[shop_id]['title'] for shop_id in self.shop_ids]
        self.avatar_urls = [shop_infos[shop_id]['avatar_url'] for shop_id in self.shop_ids]
        s = time.time()
        self.post_idss = [get_content_post_ids(shop_id) for shop_id in self.shop_ids]
        print('%s: %s' % ('Get content post id', time.time() - s))
        s = time.time()
        self.thumbnailss = [get_user_thubmnail_post_id(shop_id) for shop_id in self.shop_ids]
        print('%s: %s' % ('Get user thumbnail post id', time.time() - s))

    def get_json_serializable_data(self):
        return {
            'shop_ids':self.shop_ids,
            'header':self.header,
            'titles':self.titles,
            'avatar_urls':self.avatar_urls,
            'post_idss':self.post_idss,
            'thumbnail_post_idss':self.thumbnailss
        }

    def render(self):
        return {
            'id':self.id,
            'sub_id': self.sub_id,
            'type':'shop_component',
            'header':self.header,
            'metadata':{
                'data':[
                    {
                        'id':self.id+'_'+str(i),
                        'title':self.titles[i],
                        'avatar_url':self.avatar_urls[i],
                        'thumbnail_post_ids':self.thumbnailss[i],
                        'post_ids':self.thumbnailss[i] + [pid for pid in self.post_idss[i] if pid not in self.thumbnailss[i]]
                    }
                    # for title, url, thumbnail_post_ids, post_ids in zip(self.titles, self.avatar_urls, self.thumbnailss, self.post_idss)
                    for i in range(len(self.titles))
                ]
            }
        }

@register_home_component('common_shop')
class CommonShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id='shop_shop'
        s = time.time()
        male_item = bool(kwargs.get('male_item', False))
        self.shop_ids, self.header = get_common_shop_data(male_item)
        print('%s: %s' % ('Get shop data', time.time() - s))
        s = time.time()
        self.refresh_detail_from_shop_ids()
        print('%s: %s\n' % ('Refresh shop data', time.time() - s))

    def render(self):
        tuples = list(zip(self.titles, self.avatar_urls, self.thumbnailss, self.post_idss))
        random.shuffle(tuples)
        return {
            'id':self.id,
            'type':'shop_component',
            'header':self.header,
            'metadata':{
                'data':[
                    {
                        'id':self.id+'_'+str(i),
                        'title':tuples[i][0],
                        'avatar_url':tuples[i][1],
                        'thumbnail_post_ids':tuples[i][2],
                        'post_ids':tuples[i][2] + [pid for pid in tuples[i][3] if pid not in tuples[i][2]]
                    }
                    # for title, url, thumbnail_post_ids, post_ids in tuples
                    for i in range(len(tuples))
                ]
            }
        }


@register_home_component('merchandise_offline_shop')
class MerchandiseOfflineShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        user_id = kwargs.get('user_id', None)
        if type(user_id) != int:
            raise ValueError('User id should be interger, receive %s' % str(type(user_id)))
        self.id='merchandise_offline_shop'
        
        s = time.time()
        self.shop_ids, self.header = get_merchandise_offline_shop(user_id)
        print('%s: %s' % ('Get merchandise shop data', time.time() - s))
        s = time.time()
        
        self.refresh_detail_from_shop_ids()
        print('%s: %s\n' % ('Refresh shop data', time.time() - s))
    
    def render(self):
        tuples = list(zip(self.titles, self.avatar_urls, self.thumbnailss, self.post_idss))
        random.shuffle(tuples)
        return {
            'id':self.id,
            'type':'shop_component',
            'header':self.header,
            'metadata':{
                'data':[
                    {
                        'id':self.id+'_'+str(i),
                        'title':tuples[i][0],
                        'avatar_url':tuples[i][1],
                        'thumbnail_post_ids':tuples[i][2],
                        'post_ids':tuples[i][2] + [pid for pid in tuples[i][3] if pid not in tuples[i][2]]
                    }
                    for i in range(len(tuples))
                ]
            }
        }


@register_home_component('merchandise_online_shop')
class MerchandiseOlineShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        user_id = kwargs.get('user_id', None)
        if type(user_id) != int:
            raise ValueError('User id should be interger, receive %s' % str(type(user_id)))
        self.id='merchandise_online_shop'
        
        s = time.time()
        self.shop_ids, self.header = get_merchandise_online_shop(user_id)
        print('%s: %s' % ('Get merchandise shop data', time.time() - s))
        s = time.time()
        
        self.refresh_detail_from_shop_ids()
        print('%s: %s' % ('Refresh shop data', time.time() - s))
    
    def render(self):
        tuples = list(zip(self.titles, self.avatar_urls, self.thumbnailss, self.post_idss))
        random.shuffle(tuples)
        return {
            'id':self.id,
            'type':'shop_component',
            'header':self.header,
            'metadata':{
                'data':[
                    {
                        'id':self.id+'_'+str(i),
                        'title':tuples[i][0],
                        'avatar_url':tuples[i][1],
                        'thumbnail_post_ids':tuples[i][2],
                        'post_ids':tuples[i][2] + [pid for pid in tuples[i][3] if pid not in tuples[i][2]]
                    }
                    for i in range(len(tuples))
                ]
            }
        }


@register_home_component('personalize_shop')
class PersonalizeShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id='shop_shop'
        user_id = kwargs.get('user_id', None)
        male_item = bool(kwargs.get('male_item', False))
        if type(user_id) != int:
            raise ValueError('User id should be interger, receive %s' % str(type(user_id)))
        self.shop_ids, self.header = get_personalize_shop_data(user_id, male_item)
        self.refresh_detail_from_shop_ids()


@register_home_component('camp_shop_t2')
class MondayShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'camp_shop_t2'
        self.sub_id = 'camp_shop_t2'
        male_item = bool(kwargs.get('male_item', False))
        weekday = datetime.datetime.now().strftime('%A')
        # weekday = 'Monday'
        self.shop_ids, self.header = get_weekly_event_shop(weekday, male_item)
        self.refresh_detail_from_shop_ids()
        

@register_home_component('flashsale_shop_t7_12h12')
class FlashDealShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'flashsale_shop_t7'
        self.sub_id = 'flashsale_shop_t7_12h12'
        self.shop_ids = CONST_MAP.flashsale_shops_t7_12h12
        flashdeal_end_time = datetime.datetime(year=2022,month=5,day=7) - datetime.datetime.now()
        hour_distance = int(flashdeal_end_time.total_seconds()) // 3600
        if hour_distance > 0:
            self.header = 'Săn Flash Deals trong %s giờ nữa' % hour_distance
        else:
            self.header = CONST_MAP.home_api_text_flashsale_t7_shop_header
        self.refresh_detail_from_shop_ids()


@register_home_component('flashsale_shop_t7_18h18')
class FlashDealShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'flashsale_shop_t7'
        self.sub_id = 'flashsale_shop_t7_18h18'
        self.shop_ids = CONST_MAP.flashsale_shops_t7_18h18
        flashdeal_end_time = datetime.datetime(year=2022,month=5,day=7) - datetime.datetime.now()
        hour_distance = int(flashdeal_end_time.total_seconds()) // 3600
        if hour_distance > 0:
            self.header = 'Săn Flash Deals trong %s giờ nữa' % hour_distance
        else:
            self.header = CONST_MAP.home_api_text_flashsale_t7_shop_header
        self.refresh_detail_from_shop_ids()


@register_home_component('flashsale_shop_t7_21h21')
class FlashDealShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'flashsale_shop_t7'
        self.sub_id = 'flashsale_shop_t7_21h21'
        self.shop_ids = CONST_MAP.flashsale_shops_t7_21h21
        flashdeal_end_time = datetime.datetime(year=2022,month=5,day=7) - datetime.datetime.now()
        hour_distance = int(flashdeal_end_time.total_seconds()) // 3600
        if hour_distance > 0:
            self.header = 'Săn Flash Deals trong %s giờ nữa' % hour_distance
        else:
            self.header = CONST_MAP.home_api_text_flashsale_t7_shop_header
        self.refresh_detail_from_shop_ids()


@register_home_component('end_of_may_shop')
class EndOfMayShopComponent(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'end_of_may_shop'
        s = time.time()

        self.header = unicodedata.normalize('NFKC','Siêu sale cuối tháng')
        self.shop_ids = CONST_MAP.eom_shop_ids
        
        print('%s: %s' % ('Get shop data', time.time() - s))
        s = time.time()
        self.refresh_detail_from_shop_ids()
        print('%s: %s\n' % ('Refresh shop data', time.time() - s))
    
    def render(self):
        tuples = list(zip(self.titles, self.avatar_urls, self.thumbnailss, self.post_idss))
        # random.shuffle(tuples)
        return {
            'id':self.id,
            'type':'shop_component',
            'header':self.header,
            'metadata':{
                'data':[
                    {
                        'id':self.id+'_'+str(i),
                        'title':tuples[i][0],
                        'avatar_url':tuples[i][1],
                        'thumbnail_post_ids':tuples[i][2],
                        'post_ids':tuples[i][2] + [pid for pid in tuples[i][3] if pid not in tuples[i][2]]
                    }
                    # for title, url, thumbnail_post_ids, post_ids in tuples
                    for i in range(len(tuples))
                ]
            }
        }


@register_home_component('june_shop_week_2')
class JuneShopWeek2Component(BaseShopComponent):
    def refresh_new_data(self, **kwargs):
        now = datetime.datetime.today().date()
    
        if datetime.date(2022, 6, 8) <= now <= datetime.date(2022, 6, 15): 
            self.id = 'june_shop_week_2'
            self.sub_id = 'june_shop_week_2'
            self.shop_ids = CONST_MAP.june_shop_week_2
            self.header = CONST_MAP.home_api_text_june_shop_week_2_header
            self.refresh_detail_from_shop_ids()


def get_weekly_event_shop(weekday='Monday', male_item=False):
    header = CONST_MAP.home_api_text_t2_shop_header
    shop_ids = get_weekly_shop(number_of_shop=CONST_MAP.post_limit_small, male_item=male_item, weekday=weekday)
    return shop_ids, header


def get_common_shop_data(male_item=False):
    header = unicodedata.normalize('NFKC','Gợi ý shop')
    shop_ids = get_common_promoted_shop(CONST_MAP.post_limit_small, male_item)
    return shop_ids, header


def get_merchandise_offline_shop(user_id: int):
    header = unicodedata.normalize('NFKC','Người thanh lý gần đây')
    shop_ids = query_consignment_candidates(user_id, True)
    return shop_ids, header


def get_merchandise_online_shop(user_id: int):
    header = unicodedata.normalize('NFKC','Người thanh lý online')
    shop_ids = query_consignment_candidates(user_id, False)
    return shop_ids, header


def get_personalize_shop_data(user_id: int, male_item: bool):
    shop_ids, user_shop_contribution_count = get_promoted_shop(user_id, male_item, 20)
    if user_shop_contribution_count > 0:
        header = unicodedata.normalize('NFKC','Shop quen cho bạn')
    else:
        header = unicodedata.normalize('NFKC','Gợi ý shop')

    return shop_ids, header


def get_shop_info(shop_ids:list[int]):
    query = '''
    select au.id, au.sss_id, au.avatar 
    from account_user au 
    where au.id in :shop_ids
    order by array_position(ARRAY[%s]::int[], au.id)
    ''' % ','.join(['%s' % id for id in shop_ids])

    res = execute_raw_query(query, shop_ids=tuple(shop_ids))
    info_map:dict[int, dict[str, str]] = {}
    for item in res:
        sid = int(item[0])
        info_map[sid] = {}
        info_map[sid]['title'] = str(item[1])
        if item[2] is None:
            info_map[sid]['avatar_url'] = ''
        else:
            avatar_url = str(item[2])
            if avatar_url.startswith('media'):
                avatar_url = minio_s3_presign_url(avatar_url)
            info_map[sid]['avatar_url'] = avatar_url
    
    reorder_info_map = {}
    for id in shop_ids:
        for key, value in info_map.items():
            if id == key:
                reorder_info_map[key]=value

    return reorder_info_map


class ShopDataSchema(Schema):
    id = fields.String(require=True)
    title = fields.String(required=True)
    avatar_url = fields.String(required=True, validate=[NullableURL()])
    thumbnail_post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)


class ShopMetadataSchema(Schema):
    data = fields.List(fields.Nested(ShopDataSchema))


class ShopComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['shop_component'])])
    header = fields.String(require=True)
    metadata = fields.Nested(ShopMetadataSchema)