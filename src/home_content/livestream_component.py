from src.home_content.utils import register_home_component
from src.const import const_map as CONST_MAP


class BaseLivestreamComponent:
    def __init__(self, **kwargs) -> None:
        self.id = None
        self.sub_id = None
        self.header = None
        serialized_json_data = kwargs.get('serialized_json_data', None)
        if serialized_json_data is None:
            self.refresh_new_data(**kwargs)

    def refresh_new_data(self, **kwargs):
        raise NotImplementedError('Should not call base hashtag class')

    def render(self):
        return {
            'id': self.id,
            'sub_id': self.sub_id,
            'type': 'live_stream_component',
            'header': self.header,
            'metadata': {
                'data': []
            }
        }


@register_home_component('livestream')
class LivestreamComponent(BaseLivestreamComponent):
    def refresh_new_data(self, **kwargs):
        self.id = 'livestream'
        self.sub_id = 'livestream'
        self.header = CONST_MAP.home_api_text_livestream_header


