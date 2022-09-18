from marshmallow.validate import OneOf
from marshmallow import Schema, fields
import re
from src.utils.firebase_utils import load_firebase_documents
import codecs
import datetime
import logging


from src.const import const_map
from src.utils.db_utils import execute_raw_query
from src.utils.s3_utils import minio_download_to_bytes, minio_s3_presign_url, minio_list_file
from src.home_content.utils import register_home_component
from src.const import const_map as CONST_MAP


deviation_logger = logging.getLogger('deviation_logger')


class BaseEventComponent:
    def __init__(self, **kwargs) -> None:
        serialized_json_data = kwargs.get('serialized_json_data', None)
        if serialized_json_data is None:
            self.refresh_event_data()
        else:
            self.events = serialized_json_data

    def refresh_event_data(self):
        raise NotImplementedError('Should not use base class')

    def get_json_serializable_data(self):
        return self.events

    def render(self):
        html = '''<p><img src="%s" alt="" width="100%%" /></p>'''
        data = []
        for banner_url, content_url, redirect_url in zip(self.events['banner_url'], self.events['content_url'], self.events['redirect_url']):
            if banner_url is not None and content_url is not None:
                data_part = {}
                data_part['banner_url'] = encode_base64(minio_s3_presign_url(banner_url))
                if content_url.startswith('media'):
                    data_part['html_code'] = encode_base64(html % minio_s3_presign_url(content_url))
                else:
                    data_part['html_code'] = encode_base64(content_url)
                if redirect_url is not None:
                    data_part['redirect_url'] = encode_base64(redirect_url)
                data.append(data_part)
        for i in range(len(data)):
            data[i]['id'] = self.id+'_'+str(i)
        return {
            'id': self.id,
            'sub_id': None,
            'type': 'event_banner',
            'metadata': {
                'data': data
            }
        }


@register_home_component('event')
class EventComponent(BaseEventComponent):
    def refresh_event_data(self):
        self.id = 'event_event'
        self.events = get_event_data()


@register_home_component('feature_event')
class FeatureEventComponent(BaseEventComponent):
    def refresh_event_data(self):
        self.id = 'feature_event'
        self.events = get_feature_event_data()


@register_home_component('discovery_event')
class DiscoveryEventComponent(BaseEventComponent):
    def refresh_event_data(self):
        self.id = 'discovery_event'
        self.events = get_discovery_event_data()


def get_event_data():
    events = {
        'banner_url': [],
        'content_url': [],
        'redirect_url': []
    }
    now = datetime.datetime.today().date()

    if datetime.date(2022, 7, 23) <= now <= datetime.date(2022, 7, 30):
        add_banner_0722_13(events)
        add_banner_0722_14(events)

    if datetime.date(2022, 7, 23) <= now <= datetime.date(2022, 7, 25):
        add_banner_0722_12(events)

    if datetime.date(2022, 7, 7) <= now <= datetime.date(2022, 7, 30):
        add_banner_0722_1(events)

    if datetime.date(2022, 7, 13) <= now <= datetime.date(2022, 8, 30):
        add_banner_0722_4(events)
        add_banner_0722_7(events)
        add_banner_0722_8(events)

    # add_kol_event(events)
    # add_leaderboard_event_data(events)
    load_headline_events_from_firebase(events, False)

    return events


def get_feature_event_data():
    events = {
        'banner_url': [],
        'content_url': [],
        'redirect_url': []
    }
    now = datetime.datetime.today().date()

    if datetime.date(2022, 7, 13) <= now <= datetime.date(2022, 8, 30):
        add_banner_0722_3(events)

    # add_discovery_event(events)
    # add_visual_search_event(events)
    # add_tutorial_events(events)
    # add_shop_tutorial_event(events)

    # event_sub_folder = ['media/icon/event/%s/' % folder_name for folder_name in const_map.home_banner_feature_list]
    # for sub_folder_path in event_sub_folder:
    #     add_simple_image_event(events, sub_folder_path)

    return events


def get_discovery_event_data():
    events = {
        'banner_url': [],
        'content_url': [],
        'redirect_url': []
    }

    add_discovery_event(events)
    return events


def add_banner_0722_14(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_14.png")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_14.png")
    events["redirect_url"].append("#user_id:866268")
    return events
    

def add_banner_0722_13(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_13.png")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_13.png")
    events["redirect_url"].append("#user_id:866268")
    return events


def add_banner_0722_12(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_12.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_12.jpg")
    events["redirect_url"].append(None)
    return events


def add_banner_0722_8(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_8.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_8.jpg")
    events["redirect_url"].append("#user_id:1005888")
    return events


def add_banner_0722_7(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_7.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_7.jpg")
    events["redirect_url"].append("#user_id:1006516")
    return events


def add_banner_0722_6(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_6.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_6.jpg")
    events["redirect_url"].append("#user_id:")
    return events


def add_banner_0722_4(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_4.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_4.jpg")
    events["redirect_url"].append("#live_streams")
    return events


def add_banner_0722_3(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_3.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_3.jpg")
    events["redirect_url"].append("#virtual_fit")
    return events


def add_banner_0722_1(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0722/banner_0722_1-1.jpg")
    events["content_url"].append("media/home_screen/event/0722/banner_0722_1-1.jpg")
    events["redirect_url"].append("#user_id:866216")
    return events


def add_banner_0622_11(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0622/0622-livestream.jpg")
    events["content_url"].append("media/home_screen/event/0622/0622-livestream.jpg")
    events["redirect_url"].append(None)
    return events


def add_banner_0622_10(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/0622/0622-camp-june-w2.jpg")
    events["content_url"].append("media/home_screen/event/0622/0622-camp-june-w2.jpg")
    events["redirect_url"].append("#home_dynamic:id-collection_banner_sea")
    return events


def add_banner_0622_8(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes("media/home_screen/event/0622/june_banner.html")
    html = html_file_bytes.decode("utf-8")
    html = transorm_s3_url(html)
    events["banner_url"].append("media/home_screen/event/0622/0622-camp-june-w1.jpg")
    events["content_url"].append(html)
    events["redirect_url"].append(None)
    return events


def add_banner_0522_14(events: dict[str, list]) -> dict[str, list]:
    pass
    html_file_bytes = minio_download_to_bytes("media/home_screen/event/0522/end_of_may.html")
    html = html_file_bytes.decode("utf-8")
    html = transorm_s3_url(html)
    events["banner_url"].append("media/home_screen/event/0522/0522_14_banner.png")
    events["content_url"].append(html)
    events["redirect_url"].append(None)
    return events


def add_banner_0522_7(events: dict[str, list]) -> dict[str, list]:
    pass
    events["banner_url"].append("media/home_screen/event/Flashdeal/0512-muahe-2.png")
    events["content_url"].append("media/home_screen/event/Flashdeal/summercamp.png")
    events["redirect_url"].append(None)
    return events


def add_banner_0522_8(events: dict[str, list]) -> dict[str, list]:
    pass
    events["banner_url"].append("media/home_screen/event/Flashdeal/0511-dang-ky-goi-sub.png")
    events["content_url"].append("media/home_screen/event/Flashdeal/0511-dang-ky-goi-sub.png")
    events["redirect_url"].append(
        "https://docs.google.com/forms/d/e/1FAIpQLScuIVwGaInjLhheUgSVks8QaOPkcQhCw6ZXNMxfbvzD8SRvkA/viewform")
    return events


def add_womensday_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes("media/home_screen/event/WomensDay/0308-event-voucher.html")
    html = html_file_bytes.decode("utf-8")
    html = transorm_s3_url(html)
    events["banner_url"].append("media/home_screen/event/WomensDay/0308-uudai-banner.jpg")
    events["content_url"].append(html)
    events["redirect_url"].append(None)
    return events


def add_back2school_event(events: dict[str, list]) -> dict[str, list]:
    events["banner_url"].append("media/home_screen/event/Back2School/Back2School_Banner.jpg")
    events["content_url"].append("media/home_screen/event/Back2School/Back2School_Banner.jpg")
    events["redirect_url"].append("#home_dynamic:id-collection_banner_school")
    return events


def add_lunar2_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes("media/home_screen/event/Lunar2/Lunar2.html")
    html = html_file_bytes.decode("utf-8")
    html = transorm_s3_url(html)
    events["banner_url"].append("media/home_screen/event/Lunar2/Lunar2_Banner.png")
    events["content_url"].append(html)
    events["redirect_url"].append(None)
    return events


def load_headline_events_from_firebase(events: dict[str, list], is_test=False) -> dict[str, list]:
    # load data from firebase
    docs = load_firebase_documents('headline')
    for doc in docs:
        # validate event
        if (not doc["enable"]):
            continue

        current_time = datetime.datetime.now(doc["start_date"].tzinfo)
        if (current_time > doc["end_date"]) | (current_time < doc["start_date"]):
            continue

        if (doc["is_test"] != is_test):  # getting prod/test event
            continue

        events['banner_url'].append(doc['image_url'])
        events['content_url'].append(doc['content'])
        if doc['redirect'] == '':
            events['redirect_url'].append(None)
        else:
            events['redirect_url'].append(doc['redirect'])
    return events


def add_shop_tutorial_event(events: dict[str, list]) -> dict[str, list]:
    events['banner_url'].append('media/home_screen/event/ShopTutorial/ShopTutorial_Banner.jpg')
    events['content_url'].append('media/home_screen/event/ShopTutorial/ShopTutorial_Content.jpg')
    events['redirect_url'].append(None)
    return events


def add_lunar_event(events: dict[str, list]) -> dict[str, list]:
    events['banner_url'].append('media/home_screen/event/Lunar/Lunar_Banner.jpg')
    events['content_url'].append('media/home_screen/event/Lunar/Lunar_Banner.jpg')
    events['redirect_url'].append('#home_dynamic:id-collection_banner_1')
    return events


def add_purple_event(events: dict[str, list]) -> dict[str, list]:
    events['banner_url'].append('media/home_screen/event/Purple/Purple_Banner.jpg')
    events['content_url'].append('media/home_screen/event/Purple/Purple_Banner.jpg')
    events['redirect_url'].append('#home_dynamic:id-collection_banner_purple')
    return events


def add_flashdeal_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes('media/home_screen/event/Flashdeal/flashdeal.html')
    html = html_file_bytes.decode('utf-8')
    html = transorm_s3_url(html)
    events['banner_url'].append('media/home_screen/event/Flashdeal/Flashdeal_Banner.png')
    events['content_url'].append('media/home_screen/event/Flashdeal/Flashdeal_Banner.png')
    events['redirect_url'].append('#home_dynamic:id-shop_flashdeal')
    return events


def add_period_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes('media/home_screen/event/Period/period.html')
    html = html_file_bytes.decode('utf-8')
    html = transorm_s3_url(html)
    events['banner_url'].append('media/home_screen/event/Period/Period_Banner.png')
    events['content_url'].append(html)
    events['redirect_url'].append(None)
    return events


def add_kol_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes('media/home_screen/event/KOL/kol.html')
    html = html_file_bytes.decode('utf-8')
    html = transorm_s3_url(html)
    events['banner_url'].append('media/home_screen/event/KOL/Banner.jpg')
    events['content_url'].append(html)
    events['redirect_url'].append(
        'https://docs.google.com/forms/d/e/1FAIpQLSfVYYYfJml4e42dO1-72UMClRArpVa-jxW8i1AyG5I-_gF7rA/viewform?usp=sf_link')
    return events


def add_discovery_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes('media/home_screen/event/Discovery/discovery.html')
    html = html_file_bytes.decode('utf-8')
    html = transorm_s3_url(html)
    events['banner_url'].append('media/home_screen/event/Discovery/Discovery1.gif')
    events['content_url'].append(html)
    events['redirect_url'].append(None)
    return events


def add_visual_search_event(events: dict[str, list]) -> dict[str, list]:
    html_file_bytes = minio_download_to_bytes('media/home_screen/event/VS/vs.html')
    html = html_file_bytes.decode('utf-8')
    html = transorm_s3_url(html)
    events['banner_url'].append('media/home_screen/event/VS/VS1.gif')
    events['content_url'].append(html)
    events['redirect_url'].append(None)
    return events


def add_leaderboard_event_data(events: dict[str, list]) -> dict[str, list]:
    today = datetime.datetime.today()
    week_index = (max(0, today.day-today.weekday()))//7 + 1
    month_index = today.month
    previous_month_index = ((today.month - 1) - 1) % 12 + 1
    month_post_id, month_post_name, month_post_avatar, month_post_shop_name = query_top_post('month')
    month_shop_id, month_shop_name, month_shop_avatar = query_top_account('month')
    week_post_id, week_post_name, week_post_avatar, week_post_shop_name = query_top_post('week')
    week_shop_id, week_shop_name, week_shop_avatar = query_top_account('week')

    html_file_bytes = minio_download_to_bytes('media/home_screen/event/Leaderboard/leaderboard.html')
    html = html_file_bytes.decode('utf-8')
    html = html.format(
        week_index=week_index, month_index=month_index, previous_month_index=previous_month_index,
        month_post_id=month_post_id, month_post_name=month_post_name, month_post_avatar=month_post_avatar, month_post_shop_name=month_post_shop_name,
        month_shop_id=month_shop_id, month_shop_name=month_shop_name, month_shop_avatar=month_shop_avatar,
        week_post_id=week_post_id, week_post_name=week_post_name, week_post_avatar=week_post_avatar, week_post_shop_name=week_post_shop_name,
        week_shop_id=week_shop_id, week_shop_name=week_shop_name, week_shop_avatar=week_shop_avatar
    )
    html = transorm_s3_url(html)

    events['banner_url'].append('media/home_screen/event/Leaderboard/PeriodLeaderboardBanner.png')
    events['content_url'].append(html)
    events['redirect_url'].append(None)
    return events


def add_tutorial_events(events: dict[str, list]) -> dict[str, list]:
    events['banner_url'].append('media/icon/event/Tutorial/Banner.jpg')
    events['content_url'].append('media/icon/event/Tutorial/Event.jpg')
    events['redirect_url'].append('#post_create')
    return events


def add_simple_image_event(events: dict[str, list], s3_event_folder: str) -> dict[str, list]:
    try:
        content = [item.object_name for item in minio_list_file(s3_event_folder)]
        banner = next((path for path in content if 'Banner' in path), None)
        content = next((path for path in content if 'Event' in path), None)
        events['banner_url'].append(banner)
        events['content_url'].append(content)
        events['redirect_url'].append(None)
    except Exception as e:
        deviation_logger.info('Home event component: cannot add event in %s' % s3_event_folder)
    return events


def transorm_s3_url(html: str) -> str:
    s3_pattern = '(minio_s3_presign_url\((.*)\))'
    found_targets = re.findall(s3_pattern, html)
    for target in found_targets:
        s3_key = target[1]
        presign_url = minio_s3_presign_url(s3_key)
        html = html.replace(target[0], presign_url)
    return html


def query_top_account(duration: str):
    query = '''
    select id, sss_id, avatar from account_user au2
    where au2.id in (
    select af.user_id
    from account_following af
    left join account_user au on au.id = af.user_id 
    where af.created_at > date_trunc('%s', current_date) - interval '1 %s'
    and  af.created_at < date_trunc('%s', current_date) - interval '3 hours'
    and au.account_level_id not in (2, 99)
    group by 1
    order by count(distinct af.followed_by) desc
    limit 1
    )''' % (duration, duration, duration)
    res = execute_raw_query(query)
    return int(res[0][0]), str(res[0][1]), str(res[0][2])


def query_top_post(duration: str):
    query = '''
    select p.id, p.item_name, m.file, au.full_name 
    from post p join media m on p.id=m.post_id 
    join account_user au on p.user_id = au.id
    where p.id in (
    with ranking_table as (
        select w.post_id, count(*) as score, max(p.caption) as caption, max(p.user_id) as user_id
        from wishlist w left join post p on p.id = w.post_id 
        where w.created_at < date_trunc('%s', current_date) - interval '3 hours'
        and w.created_at > date_trunc('%s', current_date) - interval '1 %s'
        and p.is_sold = false 
        and p.created_at > date_trunc('%s', current_date) - interval '2 %s'
        and p.user_id not in (
            select id 
            from account_user
            where account_level_id in (2, 99)
        )
        group by 1
        order by 2 desc
    ),
    temp_table as (
        select user_id, max(score) as max_score
        from ranking_table
        group by 1
        order by 2 desc
    )
    select max(rt.post_id) as post_id
    from temp_table tt left join ranking_table rt on tt.max_score = rt.score and tt.user_id = rt.user_id
    group by tt.user_id
    order by max(rt.score) desc
    limit 1
    )
    limit 1
    ''' % (duration, duration, duration, duration, duration)
    res = execute_raw_query(query)
    duration_post_id, duration_post_name, duration_post_avatar, duration_post_shop_name = int(
        res[0][0]), str(res[0][1]), str(res[0][2]), str(res[0][3])
    if len(duration_post_name) < 2:
        duration_post_name = 'Bài đăng của %s' % duration_post_shop_name
    return duration_post_id, duration_post_name, duration_post_avatar, duration_post_shop_name


def encode_base64(istr):
    b_arr = istr.encode(encoding='utf-8')
    base64_b_arr = codecs.encode(b_arr, encoding='base64')
    base64_str = base64_b_arr.decode(encoding='utf-8').replace('\n', '')
    return base64_str


class EventMetadataDataItemSchema(Schema):
    id = fields.String(require=True)
    banner_url = fields.String(require=True)
    redirect_url = fields.String()
    html_code = fields.String(required=True)


class EventMetadataSchema(Schema):
    data = fields.List(fields.Nested(EventMetadataDataItemSchema))


class EventComponentSchema(Schema):
    id = fields.String(require=True)
    sub_id = fields.String(default=None, allow_none=True, missing=None)
    index = fields.Integer(strict=True, require=True)
    type = fields.String(require=True, validate=[OneOf(['event_banner'])])
    metadata = fields.Nested(EventMetadataSchema)
