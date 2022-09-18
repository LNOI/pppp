import random
import datetime

from numpy import not_equal
from marshmallow import Schema, fields
from marshmallow.validate import URL, OneOf, Range

from src.utils.db_utils import execute_raw_query
from src.carousel.watchnext_post import get_popular_post_info
from src.common.post_info_class import PostInfo, add_post_recsys_score, add_post_score_info
from src.common.random_shuffle import random_post_info_shuffle
from src.home_content.utils import register_home_component
from src.utils.s3_utils import minio_s3_presign_url
from src.const import const_map as CONST_MAP


def get_info_maps(post_ids):
    query = '''
    select p.id, p.category_id, p.ai_metadata -> '2hand'  
    from eligible_posts p 
    where p.id in :post_ids
    '''
    res =execute_raw_query(query, post_ids=tuple(post_ids))
    cat_map = {int(pid):int(cat) if cat is not None else None for pid, cat, _ in res}
    secondhand_map = {int(pid):is_2hand for pid, cat, is_2hand in res}
    return cat_map, secondhand_map


class BaseTabFrameComponent:
    def __init__(self, **kwargs) -> None:
        self.refresh_new_data(**kwargs)
    
    def refresh_new_data(self, **kwargs) -> None:
        raise NotImplementedError('Should not use base tabframe class')

    def render(self):
        raise NotImplementedError('Should not use base tabframe class')


@register_home_component('sfashionn_tabframe_t7_cn')
class SFashionnTabframeComponent(BaseTabFrameComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='sfashionn_tabframe'

        query = '''
        select id
        from eligible_posts ep 
        where 1=1
        and ep.user_id = 699211
        '''

        res = execute_raw_query(query)

        self.post_ids = [int(i[0]) for i in res]
        self.category_map, self.secondhand_map = get_info_maps(self.post_ids)
        

    def get_json_serializable_data(self):
        return {
            'post_ids':self.post_ids
        }

    def render(self):
        random.shuffle(self.post_ids)
        post_data = []
        post_data.append({
            'id':self.id+'_0',
            'post_ids':self.post_ids,
            'text':CONST_MAP.tabframe_label_sfashionn[0]['label'],
            'icon':minio_s3_presign_url(CONST_MAP.tabframe_label_sfashionn[0]['icon'])
        })

        for index in range(1, len(CONST_MAP.tabframe_label_sfashionn)):
            cat = CONST_MAP.tabframe_label_sfashionn[index]['cat']
            cat_text = CONST_MAP.tabframe_label_sfashionn[index]['label']
            cat_icon = CONST_MAP.tabframe_label_sfashionn[index]['icon']
            post_ids = [pid for pid in self.post_ids if self.category_map[pid]==cat]
            
            if cat == 8:
                post_ids += [pid for pid in self.post_ids if self.category_map[pid] is None]
            
            if len(post_ids) <= 0:
                continue
            
            post_data.append({
                'id':self.id+'_%s' % (index),
                'post_ids': post_ids,
                'text':cat_text,
                'icon':minio_s3_presign_url(cat_icon),
            })

        return {
            'id':self.id,
            'type': 'tab_frame_component',
            'header': CONST_MAP.home_api_text_t7_cn_tabframe_header,
            'metadata': {
                'data': post_data
            }
        }


@register_home_component('camp_tabframe_t2')
class MondayTabframeComponent(BaseTabFrameComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='camp_tabframe_t2'
        male_item = bool(kwargs.get('male_item', False))
        if male_item:
            gender_ids = [1,3]
        else:
            gender_ids = [2,3]

        query = '''
        select id
        from eligible_posts ep 
        where 1=1
        and ep.ai_metadata->>'2hand' = 'true'
        and ep.gender_id in :gender_ids
        '''

        res = execute_raw_query(query, gender_ids=tuple(gender_ids))

        self.post_ids = [int(i[0]) for i in res]
        self.category_map, self.secondhand_map = get_info_maps(self.post_ids)
        

    def get_json_serializable_data(self):
        return {
            'post_ids': self.post_ids
        }

    def render(self):
        random.shuffle(self.post_ids)
        post_data = []
        post_data.append({
            'id': self.id+'_0',
            'post_ids': self.post_ids,
            'text': CONST_MAP.tabframe_label_t2[0]['label'],
            'icon': minio_s3_presign_url(CONST_MAP.tabframe_label_t2[0]['icon'])
        })

        for index in range(1, len(CONST_MAP.tabframe_label_t2)):
            cat = CONST_MAP.tabframe_label_t2[index]['cat']
            cat_text = CONST_MAP.tabframe_label_t2[index]['label']
            cat_icon = CONST_MAP.tabframe_label_t2[index]['icon']
            post_ids = [pid for pid in self.post_ids if self.category_map[pid]==cat]
            
            if cat == 8:
                post_ids += [pid for pid in self.post_ids if self.category_map[pid] is None]
            
            if len(post_ids) <= 0:
                continue
            
            post_data.append({
                'id': self.id+'_%s' % (index),
                'post_ids': post_ids,
                'text': cat_text,
                'icon': minio_s3_presign_url(cat_icon),
            })

        return {
            'id': self.id,
            'type': 'tab_frame_component',
            'header': CONST_MAP.home_api_text_t2_tabframe_header,
            'metadata': {
                'data': post_data
            }
        }


@register_home_component('sssmall_tabframe_t3')
class SSSMallTabframeComponent(BaseTabFrameComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='camp_tabframe_t3'

        query = '''
        select id
        from eligible_posts ep 
        where 1=1
        and ep.user_id = 268820
        '''

        res = execute_raw_query(query)

        self.post_ids = [int(i[0]) for i in res]
        self.category_map, self.secondhand_map = get_info_maps(self.post_ids)
        

    def get_json_serializable_data(self):
        return {
            'post_ids':self.post_ids
        }

    def render(self):
        random.shuffle(self.post_ids)
        post_data = []
        post_data.append({
            'id':self.id+'_0',
            'post_ids':self.post_ids,
            'text':CONST_MAP.tabframe_label_sssmall[0]['label'],
            'icon':minio_s3_presign_url(CONST_MAP.tabframe_label_sssmall[0]['icon'])
        })

        for index in range(1, len(CONST_MAP.tabframe_label_sssmall)):
            cat = CONST_MAP.tabframe_label_sssmall[index]['cat']
            cat_text = CONST_MAP.tabframe_label_sssmall[index]['label']
            cat_icon = CONST_MAP.tabframe_label_sssmall[index]['icon']
            post_ids = [pid for pid in self.post_ids if self.category_map[pid]==cat]
            
            if cat == 8:
                post_ids += [pid for pid in self.post_ids if self.category_map[pid] is None]
            
            if len(post_ids) <= 0:
                continue
            
            post_data.append({
                'id':self.id+'_%s' % (index),
                'post_ids': post_ids,
                'text':cat_text,
                'icon':minio_s3_presign_url(cat_icon),
            })

        return {
            'id':self.id,
            'type': 'tab_frame_component',
            'header': CONST_MAP.home_api_text_t3_tabframe_header,
            'metadata': {
                'data': post_data
            }
        }


@register_home_component('tabframe')
class TabFrameComponent(BaseTabFrameComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id='tabframe_tabframe'
        male_item = bool(kwargs.get('male_item', False))
        user_vec = kwargs.get('user_vec', None)
        filter_args = {
            'user_id':-1,
            'category': [],
            'size': [],
            'condition': [],
            'price': [],
            'sex':[1] if male_item is True else [2,3],
            'avoid_categories':[None]
        }
        post_infos = get_popular_post_info(filter_args)
        add_post_score_info(post_infos)
        if user_vec is not None:
            add_post_recsys_score(post_infos, user_vec)
        post_infos = random_post_info_shuffle(post_infos)[:999]
        self.post_ids = [pi.pid for pi in post_infos]
        self.category_map, self.secondhand_map = get_info_maps(self.post_ids)
        

    def get_json_serializable_data(self):
        return {
            'post_ids':self.post_ids
        }

    def render(self):
        random.shuffle(self.post_ids)
        post_data = []
        post_data.append({
            'id':self.id+'_0',
            'post_ids':self.post_ids,
            'text':CONST_MAP.tabframe_label[0]['label'],
            'icon':minio_s3_presign_url(CONST_MAP.tabframe_label[0]['icon'])
        })

        post_data.append({
            'id':self.id+'_1',
            'post_ids':[pid for pid in self.post_ids if self.secondhand_map[pid] is True],
            'text':CONST_MAP.tabframe_label[1]['label'],
            'icon':minio_s3_presign_url(CONST_MAP.tabframe_label[1]['icon'])
        })
        for index in range(2, len(CONST_MAP.tabframe_label)):
            cat = CONST_MAP.tabframe_label[index]['cat']
            cat_text = CONST_MAP.tabframe_label[index]['label']
            cat_icon = CONST_MAP.tabframe_label[index]['icon']
            post_ids = [pid for pid in self.post_ids if self.category_map[pid]==cat]
            if cat == 8:
                post_ids += [pid for pid in self.post_ids if self.category_map[pid] is None]
            post_data.append({
                'id':self.id+'_%s' % (index),
                'post_ids': post_ids,
                'text':cat_text,
                'icon':minio_s3_presign_url(cat_icon),
            })
        return {
            'id':self.id,
            'sub_id': None,
            'type': 'tab_frame_component',
            'header': CONST_MAP.home_api_text_tab_frame_header,
            'metadata': {
                'data': post_data
            }
        }


@register_home_component('brand_tabframe')
class BrandTabFrameComponent(BaseTabFrameComponent):
    def refresh_new_data(self, **kwargs) -> None:
        self.id = 'tabframe_brand'
        male_item = bool(kwargs.get('male_item', False))
        self.brand_infos = []
        self.other_brand_infos = {
            'brand':'SSSother',
            'name':'Khác',
            'post_ids':[],
            'logo':'media/brand/khac.png'
        }
        self.weekday = datetime.datetime.now().strftime('%A')
        # self.weekday = 'Thursday'
        if self.weekday == 'Thursday':
            extra_filter = 'pop.amount >= 300000'
        else:
            # extra_filter = '1=1'
            extra_filter = 'pop.amount >= 150000'
        
        query = '''
        with brand_info as (
        select
        replace(regexp_replace(lower(pop.brand), '[^\w]+', ''), ' ', '') as brand,
        count(*) as post_count,
        min(pop.brand) as name,
        string_agg(pop.id::text, ',' order by pop.total_favorites desc) as post_ids
        from
        post pop
        where
        pop.brand is not null
        and pop.gender_id in :gender
        and replace(regexp_replace(lower(pop.brand), '[^\w]+', ''), ' ', '') in (
        select
            replace(regexp_replace(lower(name), '[^\w]+', ''), ' ', '')
        from
            brand
        where
            regexp_replace(lower(name), '[^\w]+', '') != 'khác'
        )
        and pop.is_sold = false
        and pop.is_for_sale = true
        and %s
        and pop.id in (  select
            id
        from
            eligible_posts)
        group by
        brand
        order by
        post_count desc
        limit 40),
        processed_brand as (
        select
        *,
        replace(regexp_replace(lower(name), '[^\w]+', ''), ' ', '') as brand
        from
        brand
        where
        regexp_replace(lower(name), '[^\w]+', '') != 'khác'
        )
        select
        bi.brand,
        bi."name",
        bi.post_ids,
        pb.logo
        from
        brand_info bi
        join processed_brand pb on
        bi.brand = pb.brand
        order by
        bi.post_count desc
        ''' % extra_filter
   
        if male_item:
            gender = [1,3]
        else:
            gender = [2,3]
        res = execute_raw_query(query, gender=tuple(gender))
        for item in res:
            if len(self.brand_infos) < 20:
                if len(str(item[3])) < 1:
                    # logo_url = 'media/brand/khac.png'
                    continue
                else:
                    logo_url = str(item[3])
                post_ids = [int(i) for i in item[2].split(',')]
                post_infos = [PostInfo(pid) for pid in post_ids]
                add_post_score_info(post_infos)
                user_vec = kwargs.get('user_vec', None)
                
                if user_vec is not None:
                    add_post_recsys_score(post_infos, user_vec)
                sorted_post_ids = [pi.pid for pi in sorted(post_infos, key=lambda pi: pi.post_score_info['score'], reverse=True)]
                
                if len(sorted_post_ids) < 0:
                    continue 
                
                single_brand_info = {
                    'brand':str(item[0]),
                    'name':str(item[1]),
                    'post_ids':sorted_post_ids,
                    'logo':logo_url
                }
                self.brand_infos.append(single_brand_info)
            
            else:
                post_ids = [int(i) for i in item[2].split(',')]
                random.shuffle(post_ids)
                if len(post_ids) < 0:
                    continue 
                self.other_brand_infos['post_ids'] += post_ids

    def render(self):
        post_data = []
        for brand_info in self.brand_infos:
            post_data.append({
                'id':self.id+'_%s' % (brand_info['brand']),
                'post_ids': brand_info['post_ids'],
                'text':brand_info['name'],
                'icon':minio_s3_presign_url(brand_info['logo']),
            })
        
        brand_info = self.other_brand_infos
        post_data.append({
            'id':self.id+'_other',
            'post_ids': self.other_brand_infos['post_ids'],
            'text':self.other_brand_infos['name'],
            'icon':minio_s3_presign_url(self.other_brand_infos['logo']),
        })

        if self.weekday == 'Thursday':
            header = CONST_MAP.home_api_text_t5_tabframe_header
        else:
            header = CONST_MAP.home_api_text_brand_tab_frame_header

        return {
            'id':self.id,
            'sub_id': 'tabframe_t5',
            'type': 'tab_frame_component',
            'header': header,
            'metadata': {
                'data': post_data
            }
        }


class TabframeDataSchema(Schema):
    id = fields.String(require=True)
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), require=True)
    text = fields.String(require=True)
    icon = fields.String(require=True)


class TabframeMetadataSchema(Schema):
    data = fields.List(fields.Nested(TabframeDataSchema))


class TabframeComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['tab_frame_component'])])
    header = fields.String(require=True)
    metadata = fields.Nested(TabframeMetadataSchema)
