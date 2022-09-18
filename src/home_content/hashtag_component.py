import unicodedata
import datetime
import random

from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP

from src.carousel.common import get_content_post_ids
from src.carousel.cheap_2hand import get_cheap_2hand_info
from src.carousel.recent_2hand import get_recent_2hand_post_info
from src.carousel.sss_mall import get_sss_mall_user
from src.carousel.watchnext_post import get_following_post_info, get_newpost_info
from src.carousel.misc_posts import get_hashtag_like_ordered_post_info
from src.carousel.male_items import get_processed_male_item_infos
from src.carousel.nearby_items import get_nearby_post_info, get_merchandise_post_info, get_flashsale_post_info, get_flashsale_shop_info

from src.common.more_utils import get_user_gender_id
from src.common.post_info_class import PostInfo, add_post_recsys_score, add_post_score_info, add_post_score_info_to_source_map
from src.common.random_shuffle import random_post_info_shuffle, random_shuffle

from src.popular.get_popular import get_popular_hashtag_v2
from src.recommendation.source.recsys_source import new_recsys_today_index_source
from src.home_content.utils import register_home_component
from src.home_content.banner_component import post_from_keyword
from src.utils.query.user_post import get_user_post_info


class BaseHashtagComponent:
    def __init__(self, **kwargs) -> None:
        self.sub_id = None
        
        serialized_json_data = kwargs.get('serialized_json_data', None)
        if serialized_json_data is None:
            self.refresh_new_data(**kwargs)
        else:
            self.header = serialized_json_data['header']
            self.hashtags = serialized_json_data['hashtags']
            self.subtitles = serialized_json_data['subtitles']
            self.post_idss = serialized_json_data['post_idss']
            self.shuffle_scoress = serialized_json_data['shuffle_scoress']

    def refresh_new_data(self, **kwargs):
        raise NotImplementedError('Should not call base hashtag class')

    def get_json_serializable_data(self):
        return {
            'header': self.header,
            'hashtags': self.hashtags,
            'subtitles': self.subtitles,
            'post_idss': self.post_idss,
            'shuffle_scoress': self.shuffle_scoress
        }

    def render(self):
        return {
        'id': self.id,
        'sub_id': self.sub_id,
        'type': 'hashtag_component',
        'header': self.header,
        'metadata': {
            'data': [
                {
                    'id':self.id+'_'+str(i),
                    'hashtag':self.hashtags[i] if (len(self.hashtags[i]) >=1 and self.hashtags[i][0] == '#') else '#' + self.hashtags[i],
                    'subtitle':self.subtitles[i],
                    'post_ids':random_shuffle(self.post_idss[i], self.shuffle_scoress[i])
                }
                # for hashtag, subtitle, post_ids, scores in zip(self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress)
                for i in range(len(self.hashtags))
            ]
        }
    }


@register_home_component('hashtag')
class HashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='hashtag_hashtag'
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_hashtag_data()


@register_home_component('banner_hashtag')
class BannerHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='banner_hashtag'
        male_item = bool(kwargs.get('male_item', False))
        user_vec = kwargs.get('user_vec', None)
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_banner_data(male_item, user_vec)


@register_home_component('personalize_hashtag')
class PersonalizeHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='personalize_hashtag'
        male_item = bool(kwargs.get('male_item', False))
        user_id = kwargs.get('user_id', None)
        if type(user_id) != int:
            raise ValueError('User id should be interger, receive %s' % str(type(user_id)))
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_personalize_data(user_id, male_item)


@register_home_component('merchandise_hashtag')
class MerchandiseHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='merchandise_hashtag'
        male_item = bool(kwargs.get('male_item', False))
        user_id = kwargs.get('user_id', None)
        if type(user_id) != int:
            raise ValueError('User id should be interger, receive %s' % str(type(user_id)))
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_merchandise_data(user_id, male_item)


@register_home_component('empty_title_hashtag')
class EmptyTitleHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.header = str(kwargs.get('title'))
        self.id='title_hashtag_%s' % (str(kwargs.get('title')))
        self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = [''], [''], [[]], [[]]


@register_home_component('like_ordered_hashtag')
class TestLikeOrderedHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='like_ordered_hashtag'
        male_item = bool(kwargs.get('male_item', False))
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_like_orderded_data(male_item)


@register_home_component('flashsale_hashtag_t6')
class BannerHashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'flashsale_hashtag_t6'
        self.sub_id = 'flashsale_hashtag_t6'
        male_item = bool(kwargs.get('male_item', False))
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_flashsale_data(male_item)


@register_home_component('flashsale_shop_hashtag_t7_12h12')
class HashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'flashsale_shop_hashtag_t7'
        self.sub_id = 'flashsale_hashtag_t7_12h12'
        male_item = bool(kwargs.get('male_item', False))
        shop_ids = CONST_MAP.flashsale_shops_t7_12h12
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_flashsale_shop_data(male_item, shop_ids)
        self.subtitles = ['12:12 SIÊU SALE 70%' for subtitle in self.subtitles]


@register_home_component('flashsale_shop_hashtag_t7_18h18')
class HashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='flashsale_shop_hashtag_t7'
        self.sub_id = 'flashsale_hashtag_t7_18h18'
        male_item = bool(kwargs.get('male_item', False))
        shop_ids = CONST_MAP.flashsale_shops_t7_18h18
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_flashsale_shop_data(male_item, shop_ids)
        self.subtitles = ['18:18 SALE UPTO 70%' for subtitle in self.subtitles]


@register_home_component('flashsale_shop_hashtag_t7_21h21')
class HashtagComponent(BaseHashtagComponent):
    def refresh_new_data(self, **kwargs):
        self.id='flashsale_shop_hashtag_t7'
        self.sub_id = 'flashsale_hashtag_t7_21h21'
        male_item = bool(kwargs.get('male_item', False))
        shop_ids = CONST_MAP.flashsale_shops_t7_21h21
        self.header, self.hashtags, self.subtitles, self.post_idss, self.shuffle_scoress = get_flashsale_shop_data(male_item, shop_ids)
        self.subtitles = ['21:21 SALE UPTO 70%' for subtitle in self.subtitles]


def get_like_orderded_data(male_item):
    like_ordered_post_infos = get_hashtag_like_ordered_post_info([15863], for_sale=False)
    like_ordered_post_ids = [pi.pid for pi in like_ordered_post_infos]
    header = 'Khoe đồ chơi Tết - Nhận xu mê mệt'
    hashtags = ['#TetMacGi']
    
    subtitles = ['Khoe outfit Tết để nhận ngay 50 000 xu']
    post_idss = [
        like_ordered_post_ids[:399]
    ]
    scoress = [
        []
    ]
    return header, hashtags, subtitles, post_idss, scoress


def get_test_data(male_item):
    filter_args = {
        'time_limit':3, 'category':[], 'size':[], 'condition':[], 'sex':[], 'price':[], 'user_id':-1
    }
    new_post_infos = get_newpost_info(filter_args)
    
    source_candidate_map = {'newpost':new_post_infos}
    add_post_score_info_to_source_map(source_candidate_map)
    for source in source_candidate_map:
        source_candidate_map[source] = random_post_info_shuffle(source_candidate_map[source])
    
    purple_post_ids = CONST_MAP.purple_post_ids.copy()
    random.shuffle(purple_post_ids)

    summer_post_ids = post_from_keyword(['đi biển', 'đầm dây', 'maxi', 'Đầm hở lưng', 'Áo hở lưng', 'váy voan', 'Đầm voan hoa', 'chân váy voan', 'đầm voan dây', 'sơ mi họa tiết', 'bikini', 'áo dây', 'túi cói', 'nón cói', 'mũ cói', 'sandal', 'sandals', 'đồ bơi', 'tote'], [])
    random.shuffle(summer_post_ids)
    workplace_post_ids = post_from_keyword(['áo len tăm', 'áo thun cổ trụ', 'áo sơ mi', 'sơ mi lụa', 'sơ mi trắng', 'công sở', 'chân váy chữ A', 'quần tây', 'quần suông', 'đầm sơ mi', 'vest', 'blazer', 'túi da', 'giày cao gót 5cm', 'giày mary janes', 'giày da', 'giày búp bê'], ['bơi', 'bikini'])
    random.shuffle(workplace_post_ids)

    header = 'Test newpost component.'
    hashtags = ['#newpost', '#purple', '#summer', '#workplace']
    
    subtitles = ['Test newpost hashtag', 'Keyword thời trang màu tím', 'Keyword thời trang xuân hè', 'Keyword thời trang công sở']
    post_idss = [
        [pi.pid for pi in source_candidate_map['newpost'][:399]],
        purple_post_ids[:399],
        summer_post_ids[:399],
        workplace_post_ids[:399],
    ]
    scoress = [
        [pi.post_score_info['score'] for pi in source_candidate_map['newpost'][:399]],
        [1]*len(purple_post_ids[:399]),
        [1]*len(summer_post_ids[:399]),
        [1]*len(workplace_post_ids[:399]),
    ]
    return header, hashtags, subtitles, post_idss, scoress


def get_hashtag_data():
    hashtag_data = get_popular_hashtag_v2(10)
    hashtag_data = [i for i in hashtag_data if i['hashtag'] not in ['#HàngHiệu', '#2handMớiVề', '#CựcRẻ']]
    hashtags = [item['hashtag'] for item in hashtag_data]
    subtitles = [item['subtitle'] for item in hashtag_data]
    post_idss = [item['post_id'] for item in hashtag_data]
    shuffle_scoress = [[] for item in hashtag_data]
    return CONST_MAP.home_api_text_hashtag_header, hashtags, subtitles, post_idss, shuffle_scoress


def get_banner_data(male_item, user_vec=None):
    header = CONST_MAP.home_api_text_banner_header
    hashtags = [
        # CONST_MAP.home_api_text_banner_luxury,
        CONST_MAP.home_api_text_banner_sssmall,
        CONST_MAP.home_api_text_banner_cheap,
        CONST_MAP.home_api_text_banner_recent
        ]
    hashtags = ['#' + i for i in hashtags]
    
    subtitles = [
        # CONST_MAP.home_api_text_banner_luxury_subtitle,
        CONST_MAP.home_api_text_banner_sssmall_subtitle,
        CONST_MAP.home_api_text_banner_cheap_subtitle,
        CONST_MAP.home_api_text_banner_recent_subtitle
    ]
    
    sss_mall_user_ids = get_sss_mall_user(male_item)
    sss_mall_post_ids = [pid for uid in sss_mall_user_ids for pid in get_content_post_ids(uid)]
    
    cheap_post_infos = get_cheap_2hand_info(male_item)
    # luxury_post_infos = get_luxury_2hand_post_info(male_item)
    recent_post_infos = get_recent_2hand_post_info(male_item)
    source_candidate_map = {
        'cheap':cheap_post_infos,
        # 'luxury':luxury_post_infos,
        'recent':recent_post_infos
    }
    add_post_score_info_to_source_map(source_candidate_map)
    if user_vec is not None:
        post_infos = []
        for source in source_candidate_map:
            post_infos += source_candidate_map[source]
        add_post_recsys_score(post_infos, user_vec)
    for source in source_candidate_map:
        source_candidate_map[source] = random_post_info_shuffle(source_candidate_map[source])

    post_idss = [
        # [pi.pid for pi in source_candidate_map['luxury'][:99]],
        sss_mall_post_ids[:299],
        [pi.pid for pi in source_candidate_map['cheap'][:99]],
        [pi.pid for pi in source_candidate_map['recent'][:99]],
    ]

    scoress = [
        # [pi.post_score_info['score'] for pi in source_candidate_map['luxury'][:99]],
        [],
        [pi.post_score_info['score'] for pi in source_candidate_map['cheap'][:99]],
        [pi.post_score_info['score'] for pi in source_candidate_map['recent'][:99]]
    ]
    
    return header, hashtags, subtitles, post_idss, scoress


def get_personalize_data(user_id, male_item):
    header = CONST_MAP.home_api_text_personalize_hashtag_header
    hashtags = [
        unicodedata.normalize('NFKC','#Chọn đồ giúp bạn'),
        unicodedata.normalize('NFKC','#Thời trang quanh bạn'),
        unicodedata.normalize('NFKC','#Follower')
    ]

    subtitles = [
        CONST_MAP.home_api_text_personalize_hashtag_recsys,
        CONST_MAP.home_api_text_personalize_hashtag_nearby,
        CONST_MAP.home_api_text_personalize_hashtag_follower
    ]

    recsys_post_info = new_recsys_today_index_source(user_id)[:CONST_MAP.post_limit_small]
    nearby_item_info = get_nearby_post_info(user_id, male_item)
    add_post_score_info(nearby_item_info)
    nearby_item_info = random_post_info_shuffle(nearby_item_info)[:CONST_MAP.post_limit_small]
    
    following_post_info = get_following_post_info(user_id, None)[:CONST_MAP.post_limit_small]
    post_idss = [
        [pi.pid for pi in recsys_post_info],
        [pi.pid for pi in nearby_item_info],
        [pi.pid for pi in following_post_info]
    ]
    scoress = [
        [pi.post_score_info['score'] for pi in recsys_post_info],
        [pi.post_score_info['score'] for pi in nearby_item_info],
        []
    ]
    if male_item: #get_user_gender_id(user_id) != 2:
        hashtags.insert(1, unicodedata.normalize('NFKC','#Đồ nam'))
        subtitles.insert(1, CONST_MAP.home_api_text_personalize_hashtag_male_item)
        male_item_info = [PostInfo(value_map=pi_json) for pi_json in get_processed_male_item_infos()]
        post_idss.insert(1, [pi.pid for pi in male_item_info])
        scoress.insert(1, [pi.post_score_info['score'] for pi in male_item_info])

    return header, hashtags, subtitles, post_idss, scoress


def get_merchandise_data(user_id, male_item):
    header = CONST_MAP.home_api_text_merchandise_hashtag_header
    hashtags = [
        unicodedata.normalize('NFKC','#Hàng tốt ở gần'),
        #unicodedata.normalize('NFKC','#Người thanh lý gần đây'),
        unicodedata.normalize('NFKC','#Hàng tốt khắp nơi')
        #unicodedata.normalize('NFKC','#Người thanh lý khắp nơi')
    ]

    subtitles = [
        unicodedata.normalize('NFKC','#Thu mua offline'),
        #unicodedata.normalize('NFKC','#Thu mua offline'),
        unicodedata.normalize('NFKC','#Thu mua online'),
        #unicodedata.normalize('NFKC','#Thu mua online')
    ]

    offline_item_info = get_merchandise_post_info(user_id, male_item, 2, 150000)
    add_post_score_info(offline_item_info)
    offline_item_info = random_post_info_shuffle(offline_item_info)[:CONST_MAP.post_limit_small]
    
    online_item_info = get_merchandise_post_info(user_id, male_item, 0, 150000)
    add_post_score_info(online_item_info)
    online_item_info = random_post_info_shuffle(online_item_info)[:CONST_MAP.post_limit_small]

    post_idss = [
        [pi.pid for pi in offline_item_info],
        [pi.pid for pi in online_item_info]
    ]
    scoress = [
        [pi.post_score_info['score'] for pi in offline_item_info],
        [pi.post_score_info['score'] for pi in online_item_info],
    ]

    return header, hashtags, subtitles, post_idss, scoress


def get_flashsale_data(male_item):
    header = CONST_MAP.home_api_text_flashsale_t6_hashtag_header
    hashtags = [
        unicodedata.normalize('NFKC','#49k'),
        unicodedata.normalize('NFKC','#79k'),
        unicodedata.normalize('NFKC','#99k')
    ]

    subtitles = [
        unicodedata.normalize('NFKC','Sale lớn đồng giá'),
        unicodedata.normalize('NFKC','Số lượng giới hạn'),
        unicodedata.normalize('NFKC','Chỉ trong hôm nay')
    ]

    shop_ids = CONST_MAP.flashsale_shops_t6
    limit_item = CONST_MAP.post_limit_small

    flashsale1_item_info = get_flashsale_post_info(male_item=male_item, shop_ids=shop_ids, price_list=[49000])
    add_post_score_info(flashsale1_item_info)
    # flashsale1_item_info = random_post_info_shuffle(flashsale1_item_info)[:limit_item]
    flashsale1_item_info = flashsale1_item_info[:limit_item]

    flashsale2_item_info = get_flashsale_post_info(male_item=male_item, shop_ids=shop_ids, price_list=[79000])
    add_post_score_info(flashsale2_item_info)
    # flashsale2_item_info = random_post_info_shuffle(flashsale2_item_info)[:limit_item]
    flashsale2_item_info = flashsale2_item_info[:limit_item]

    flashsale3_item_info = get_flashsale_post_info(male_item=male_item, shop_ids=shop_ids, price_list=[99000])
    add_post_score_info(flashsale3_item_info)
    # flashsale3_item_info = random_post_info_shuffle(flashsale3_item_info)[:limit_item]
    flashsale3_item_info = flashsale3_item_info[:limit_item]

    post_idss = [
        [pi.pid for pi in flashsale1_item_info],
        [pi.pid for pi in flashsale2_item_info],
        [pi.pid for pi in flashsale3_item_info]
    ]
    scoress = [
        [pi.post_score_info['score'] for pi in flashsale1_item_info],
        [pi.post_score_info['score'] for pi in flashsale2_item_info],
        [pi.post_score_info['score'] for pi in flashsale3_item_info]
    ]

    return header, hashtags, subtitles, post_idss, scoress


def get_flashsale_shop_data(male_item, shop_ids):
    header = CONST_MAP.home_api_text_flashsale_t7_shop_header
    hashtag_data = get_flashsale_shop_info(number_of_hashtag=5, male_item=male_item, shop_ids=shop_ids)
    # hashtag_data = [i for i in hashtag_data if i['hashtag'] not in ['#HàngHiệu', '#2handMớiVề', '#CựcRẻ']]
    hashtags = [item['hashtag'] for item in hashtag_data]
    subtitles = [item['subtitle'] for item in hashtag_data]
    post_idss = [item['post_id'] for item in hashtag_data]
    shuffle_scoress = [[] for item in hashtag_data]
    return header, hashtags, subtitles, post_idss, shuffle_scoress


from marshmallow import Schema, fields
from marshmallow.validate import Range, OneOf
class HashtagDataSchema(Schema):
    id = fields.String(require=True)
    hashtag = fields.String(required=True)
    subtitle = fields.String(required=True)
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)

class HashtagMetadataSchema(Schema):
    data = fields.List(fields.Nested(HashtagDataSchema))

class HashtagComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['hashtag_component'])])
    header = fields.String(require=True)
    metadata = fields.Nested(HashtagMetadataSchema)