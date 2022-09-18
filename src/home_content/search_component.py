from src.popular.get_popular import get_popular_keyword_v2
from src.const import const_map as CONST_MAP
from src.home_content.utils import register_home_component

@register_home_component('search')
class SearchComponent:
    def __init__(self, **kwargs) -> None:
        serialized_json_data = kwargs.get('serialized_json_data', None)
        self.id='search_search'
        if serialized_json_data is None:
            self.keyword_data = get_popular_keyword_v2(10)
        else:
            self.post_ids = serialized_json_data

    def get_json_serializable_data(self):
        return self.keyword_data

    def render(self):
        return {
            'id':self.id,
            'sub_id': None,
            'type': 'search_component',
            'header': CONST_MAP.home_api_text_search_header,
            'metadata': {
                'data': [
                    {
                        'id':self.id+'_'+str(i),
                        'keyword':self.keyword_data[i]['keyword'],
                        'thumbnail_url':self.keyword_data[i]['image_url']
                    }
                    # for item in self.keyword_data
                    for i in range(len(self.keyword_data))
                ]
            }
        }

from marshmallow import Schema, fields
from marshmallow.validate import URL, OneOf
class SearchDataSchema(Schema):
    id = fields.String(require=True)
    keyword = fields.String(required=True)
    thumbnail_url = fields.String(required=True, validate=[URL()])

class SearchMetadataSchema(Schema):
    data = fields.List(fields.Nested(SearchDataSchema))

class SearchComponentSchema(Schema):
    id = fields.String(require=True)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['search_component'])])
    header = fields.String(require=True)
    metadata = fields.Nested(SearchMetadataSchema)