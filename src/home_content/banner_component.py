import unicodedata
import random
import datetime
import logging

from typing import Optional
from marshmallow import Schema, fields
from marshmallow.validate import Range, OneOf, URL

from src.carousel.common import get_represent_shop_id_from_post_ids, get_june_week_2_post_ids
from src.carousel.misc_posts import get_caption_filtered_post_info
from src.carousel.kol_post import kol_result
from src.common.post_info_class import add_post_recsys_score, add_post_score_info
from src.common.random_shuffle import random_post_info_shuffle
from src.common.source.kol_source import check_recent_kol
from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP
from src.home_content.utils import register_home_component
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_s3_presign_url


deviation_logger = logging.getLogger('deviation_logger')


class BaseBannerComponent:
    def __init__(self, **kwargs) -> None:
        serialized_json_data = kwargs.get('serialized_json_data', None)
        male_item = bool(kwargs.get('male_item', False))
        if serialized_json_data is None:
            self.refresh_new_data(**kwargs)
        else:
            self.header = serialized_json_data['header']
            self.texts = serialized_json_data['texts']
            self.thumbnail_urls = serialized_json_data['thumbnail_urls']
            self.post_idss = serialized_json_data['post_idss']
            self.shop_idss = serialized_json_data['shop_idss']
    
    def refresh_new_data(self, **kwargs):
        raise NotImplementedError('Should not call base banner class')

    def get_json_serializable_data(self):
        return {
            'header':self.header,
            'texts':self.texts,
            'thumbnail_urls':self.thumbnail_urls,
            'post_idss':self.post_idss,
            'shop_idss':self.shop_idss
        }
    
    def render(self):
        return {
            'id':self.id,
            'sub_id': None,
            'type':'banner_component',
            'header': self.header,
            'metadata': {
                'data':[
                    {
                        'id':self.id+'_'+str(self.ids[i]),
                        'text': self.texts[i],
                        'thumbnail_url': self.thumbnail_urls[i],
                        'post_ids': self.post_idss[i],
                        'shop_ids': self.shop_idss[i]
                    }
                    for i in range(len(self.texts))
                ]
            }
        }


@register_home_component('kol_banner')
class KOLBannerComponent(BaseBannerComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='kol_banner'
        male_item = bool(kwargs.get('male_item', False))
        user_vec = kwargs.get('user_vec', None)
        self.ids, self.header, self.texts, self.thumbnail_urls, self.post_idss, self.shop_idss = get_kol_data(male_item, user_vec)


@register_home_component('collection_banner')
class CollectionBannerComponent(BaseBannerComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='collection_banner'
        male_item = bool(kwargs.get('male_item', False))
        user_vec = kwargs.get('user_vec', None)
        self.ids, self.header, self.texts, self.thumbnail_urls, self.post_idss, self.shop_idss = get_collection_data(male_item, user_vec)


def get_kol_data(male_item, user_vec=None):
    total_pi = kol_result(male_item)
    pid_uid_map = {}
    uid_avatar_map = {}
    uid_full_name_map = {}
    uid_timestamp = {}
    for pi in total_pi:
        i_uid = pi.source_specific_info['uid']
        pid_uid_map[int(pi.pid)] = i_uid
        if i_uid not in uid_avatar_map:
            uid_avatar_map[i_uid] = str(pi.source_specific_info['avatar_url'])
            uid_full_name_map[i_uid] = str(pi.source_specific_info['full_name'])
        if i_uid not in uid_timestamp:
            uid_timestamp[i_uid] = pi.source_specific_info['timestamp']
        if uid_timestamp[i_uid] < pi.source_specific_info['timestamp']:
            uid_timestamp[i_uid] = pi.source_specific_info['timestamp']
    
    # # order by gender -> account create date -> post create date
    uids = list(uid_timestamp.keys())

    # # # Sort post from lastest to old
    # uids = sorted(uid_timestamp, key=uid_timestamp.get, reverse=True)

    # Sort 2,1,3 (bothside UX)
    # uids = list(uid_timestamp.keys())
    # y = uids.copy()
    # n = len(uids)
    # for i in range(n):
    #     if i % 2 == 0:
    #         y[i//2] = uids[i]    
    #     else:
    #         y[n - 1 - i//2] = uids[i]
    # for i in range(1, n):
    #     if i % 2 == 0:
    #         y[n - i//2] = uids[i]
    #     else:
    #         y[i//2 + 1] = uids[i]
    # uids = y
    # avatars = [minio_s3_presign_url(uid_avatar_map[uid], cache_refresh=True) for uid in uids]
    avatars = []
    for uid in uids:
        avatars.append(minio_s3_presign_url(uid_avatar_map[uid]))

    full_names = [uid_full_name_map[uid] for uid in uids]
    add_post_score_info(total_pi)
    if user_vec is not None:
        add_post_recsys_score(total_pi, user_vec)
    pi_lists = [[pi for pi in total_pi if pid_uid_map[pi.pid] == uid] for uid in uids]
    pi_lists = [random_post_info_shuffle(pi_list) for pi_list in pi_lists]
    post_idss = [[pi.pid for pi in pis] for pis in pi_lists]
    shop_idss = [[uid, 268820] for uid in uids]

    return list(range(len(full_names))), CONST_MAP.home_api_text_kol_header, full_names, avatars, post_idss, shop_idss


def get_collection_data(male_item, user_vec=None):
    header=CONST_MAP.home_api_text_collection_banner_header
    texts = []
    thumbnails = []
    post_idss = []
    ids=[]
    for collection_name in CONST_MAP.collection_config_june:
        collection = CONST_MAP.collection_config_june[collection_name]
        ids.append(collection['id'])
        texts.append(collection['text'])
        thumbnails.append(minio_s3_presign_url(collection['thumbnail']))
        curating_post_ids = []
        for curating_acc_info in collection['curating_acc']:
            curating_post_ids += post_from_curating_acc(curating_acc_info['id'], collection['keywords'], curating_acc_info['start'], curating_acc_info['end'])
        keyword_post_ids = post_from_keyword(collection['keywords'], collection['avoid_keywords'])

        now = datetime.datetime.today().date()
    
        if (datetime.date(2022, 6, 8) <= now <= datetime.date(2022, 6, 15)) and collection_name == 'sea':
            shop_results = get_june_week_2_post_ids(CONST_MAP.june_shop_week_2)
            june_post_ids = [pid for record in shop_results for pid in record[1]]
            keyword_post_ids = keyword_post_ids + june_post_ids
            random.shuffle(keyword_post_ids)

        total_post_ids = list(dict.fromkeys(curating_post_ids + keyword_post_ids))
        if len(curating_post_ids) > 0 and len(keyword_post_ids) > 0:
            post_idss.append(total_post_ids[:400])
        else:
            post_idss.append(total_post_ids[:200])

    shop_idss = [get_represent_shop_id_from_post_ids(post_ids) for post_ids in post_idss]
    return ids, header, texts, thumbnails, post_idss, shop_idss


def post_from_keyword(keywords:list[str], avoid_keywords:list[str]) -> list[int]:
    post_ids = []
    for keyword in keywords:
        try:
            keyword_res = RESOURCE_MAP['solr_search_client'].search(unicodedata.normalize('NFKC',keyword), **{'rows': 50 * 3, 'fq':'type:post', 'q.op':'OR', 'defType':'edismax'})
            post_ids += [int(kr['id'].split('_')[-1]) for kr in keyword_res]
        except Exception as e:
            deviation_logger.info('Collection banner: Solr search error: keyword %s: %s' % (keyword, str(e)), exc_info=True)
    post_ids = list(set(post_ids))
    post_ids = [pi.pid for pi in get_caption_filtered_post_info(post_ids, avoid_keywords)]
    random.shuffle(post_ids)
    return post_ids


def post_from_curating_acc(curating_acc:int, filtered_keywords: list, start:str, end:Optional[str]) -> list[int]:
    if end is None:
        end = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime(r'%d/%m/%Y')
    # query = '''
    # select post_id from wishlist w 
    # where w.user_id=:user_id
    # and w.created_at > to_date(:start, 'DD/MM/YYYY')
    # and w.created_at < to_date(:end,'DD/MM/YYYY')
    # '''

    if filtered_keywords:
        query = """
        with kw_table as (
            select
                1 as check_id,
                generate_series(0,:len_keyword),
                unnest(array%s) as word
        ),
            post_info as (
        select
            1 as check_id,
            w.post_id ,
            w.user_id ,
            w.created_at as wished_day,
            p.item_name || ' ' || p.caption  as sentence
        from
            wishlist w
        left join post p on
            w.post_id = p.id ),
            processing as (
        select
            post_id ,
            user_id ,
            wished_day,
            sentence,
            word,
            case when sentence ilike '%%'|| word || '%%' then 1 else 0 end as cate
        from
            post_info pi
        join kw_table kw on
            pi.check_id = kw.check_id)
            select distinct post_id  from processing
            where cate = 1
            and user_id = :user_id
            and wished_day > to_date(:start, 'DD/MM/YYYY')
            and wished_day < to_date(:end,'DD/MM/YYYY')
        """ % filtered_keywords
    
    else:
        query = '''
        select post_id from wishlist w 
        where w.user_id=:user_id
        and w.created_at > to_date(:start, 'DD/MM/YYYY')
        and w.created_at < to_date(:end,'DD/MM/YYYY')
        '''

    res = execute_raw_query(query, user_id=curating_acc, len_keyword=len(filtered_keywords), start=start, end=end)
    curated_post_ids = list(set([int(i[0]) for i in res]))
    random.shuffle(curated_post_ids)
    return curated_post_ids


class BannerMetaItemSchema(Schema):
    id = fields.String(require=True)
    text = fields.String(require=True)
    thumbnail_url = fields.String(require=True, validate=[URL()])
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)
    shop_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)

class BannerMetadataSchema(Schema):
    data = fields.List(fields.Nested(BannerMetaItemSchema))

class BannerComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['banner_component'])])
    header = fields.String(require=True)
    metadata = fields.Nested(BannerMetadataSchema)
