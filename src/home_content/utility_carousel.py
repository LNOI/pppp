from marshmallow import Schema, fields
from marshmallow.validate import URL, OneOf, Range

from src.utils.marshmallow_utils import UnionField
from src.utils.s3_utils import minio_s3_presign_url
from src.carousel.sss_mall import SSSMallShopSchema
from src.carousel.voucher_post import get_processed_voucher_post_infos
from src.carousel.common import get_represent_shop_id_from_post_ids
from src.const import const_map as CONST_MAP
from src.home_content.utils import register_home_component


@register_home_component('utility')
class UtilityComponent:
    def __init__(self, **kwargs) -> None:
        self.id='utility_utility'
        serialized_json_data = kwargs.get('serialized_json_data', None)
        if serialized_json_data is None:
            self.promotion_post_ids = [pi.pid for pi in get_processed_voucher_post_infos()]
            self.promotion_post_shop_ids = get_represent_shop_id_from_post_ids(self.promotion_post_ids)

            # self.vf_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/fittingroom.jpg')
            # self.livestream_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/livestream.png')
            # self.point_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/bonbonxu.png')
            # self.voucher_mngt_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/voucher.png')
            # self.leaderboard_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/leaderboard.png')
            # self.visual_search_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons/visualsearch.png')

            self.point_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/bonbonxu.png')
            self.voucher_mngt_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/voucher.png')
            self.leaderboard_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/leaderboard.png')
            self.visual_search_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/visualsearch.png')
            self.livestream_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/livestream.png')
            self.vf_thumbnail_url = minio_s3_presign_url('media/icon/carousel_icons_rebrand_0722/fittingroom.png')
        else:
            self.promotion_post_ids, self.promotion_post_shop_ids = serialized_json_data['promotion']
            self.point_thumbnail_url = serialized_json_data['thumbnail_url'][0]
            self.voucher_mngt_thumbnail_url = serialized_json_data['thumbnail_url'][1]
            self.leaderboard_thumbnail_url = serialized_json_data['thumbnail_url'][2]
            self.visual_search_thumbnail_url = serialized_json_data['thumbnail_url'][6]
    
    def get_json_serializable_data(self):
        return {
            'promotion':[self.promotion_post_ids, self.promotion_post_shop_ids],
            'thumbnail_url':[
                self.point_thumbnail_url,
                self.voucher_mngt_thumbnail_url,
                self.leaderboard_thumbnail_url,
                self.visual_search_thumbnail_url
            ]
        }

    def render(self):
        return {
            'id':self.id,
            'sub_id': None,
            'type': 'utility_carousel',
            'metadata': {
                'data': [
                    {
                        'id': 'virtualfit',
                        'text':CONST_MAP.home_api_text_utlity_carousel_vf,
                        'thumbnail_url':self.vf_thumbnail_url,
                        'post_ids':'open',
                        'screen':'virtual_fit'
                    },
                    {
                        'id': 'ssslive',
                        'text':CONST_MAP.home_api_text_utlity_carousel_ssslive,
                        'thumbnail_url':self.livestream_thumbnail_url,
                        'post_ids':'open',
                        'screen':'livestream'
                    },
                    {
                        'id': 'bonbonxu',
                        'text':CONST_MAP.home_api_text_utlity_carousel_coin,
                        'thumbnail_url':self.point_thumbnail_url,
                        'post_ids':'open',
                        'screen':'point'
                    },
                    {
                        'id': 'voucher',
                        'text': CONST_MAP.home_api_text_utlity_carousel_voucher_screen,
                        'thumbnail_url': self.voucher_mngt_thumbnail_url,
                        'post_ids': 'open',
                        'screen': 'voucher_mngt',
                        'param': {
                            'shop_ids': self.promotion_post_shop_ids,
                            'post_ids': self.promotion_post_ids
                        }
                    },
                    {
                        'id': 'leaderboard',
                        'text': CONST_MAP.home_api_text_utlity_carousel_leaderboard,
                        'thumbnail_url': self.leaderboard_thumbnail_url,
                        'post_ids': 'open',
                        'screen': 'leaderboard'
                    },
                    {
                        'id': 'visual_search',
                        'text': CONST_MAP.home_api_text_utlity_carousel_search,
                        'thumbnail_url': self.visual_search_thumbnail_url,
                        'post_ids': 'open',
                        'screen': 'visual_search'
                    }
                ]
            }
        }


class UtilityShopParamSchema(Schema):
    shops = fields.List(fields.Nested(SSSMallShopSchema))


class UtilityPostParamSchema(Schema):
    post_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), required=True)
    shop_ids = fields.List(fields.Integer(strict=True, validate=[Range(min=1)]), required=True)


class UtilityDataSchema(Schema):
    id = fields.String(require=True)
    text = fields.String(required=True)
    thumbnail_url = fields.String(required=True, validate=[URL()])
    post_ids = fields.String(validate=[OneOf(['open'])])
    screen = fields.String(required=True)
    param = fields.Raw() #UnionField([fields.Nested(UtilityPostParamSchema), fields.Nested(UtilityShopParamSchema)])


class UtilityMetadataSchema(Schema):
    data = fields.List(fields.Nested(UtilityDataSchema))


class UtilityComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['utility_carousel'])])
    metadata = fields.Nested(UtilityMetadataSchema)
