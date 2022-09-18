import unicodedata

test_mode = True
light_mode = False
hour = 12
min = 12
dow = 5

config_file_key = 'media/server_config_file/fashion_config.json'
milvus_fallback = True
request_time = '2020-11-23T17:07:43'

faiss_api_endpoint = 'http://faiss.sssmarket.com:8661'

score_func = 'cosine'
watch_next_type = 'new'
currency_scaler_mean = 0.6005636865666579
currency_scaler_std = 1.715589095213295
image_embed_size = 1536
object_detect_img_resize = 512

popular_post_like_limit = 3
popular_post_view_limit = 30

popular_business_post_like_limit = 5
popular_business_post_view_limit = 30

dashboard_user_id: list[int] = [1006516, 1033905, 1005888]
dashboard_post_day_limit = 30
dashboard_post_limit = 10
dashboard_post_id: list[int] = []
dashboard_time_threshold = 1

shop_post_day_limit = 10

feature_user_id = [3, 71, 1134]

newpost_view_limit = 30
following_hour_limit = 24 * 7

avoid_user_id = [89, 182, 82, 6, 689, 10, 98, 183, 69, 5, 23, 708, 706, 12,
                 8, 73, 85, 120, 86, 32, 54, 524, 1, 4, 522, 532, 53, 81, 512, 207, 16, 7]
new_candidate_filter_mode = 1
recsys_candidate_number_limit = 100
recsys_candidate_control_size = 20
recsys_candidate_distance_threshold = 2

# Order and ratio config for watchnext/discovery
source_order_trending = ['popular', 'popular_business', 'featured', 'shop']
source_ratio_trending = [0.4, 0.2, 0.2, 0.2]

source_order_personalize = ['following', 'popular', 'newpost', 'shop']
source_ratio_personalize = [0.2, 0.2, 0.4, 0.2]



source_order_new = ['newpost']
source_ratio_new = [1]

#api discovery_mall
source_order_mall = ['remind', 'curator', 'discovery_mall']
source_ratio_mall = [0.2, 0.1, 0.7]

#api discovery_2hand
source_order_2hand = ['remind', 'curator', 'discovery_2hand']
source_ratio_mall = [0.2, 0.1, 0.7]
secondhand_limit_view = 512

#api discovery_new
source_order_new = ['remind', 'curator', 'discovery_new']
source_ratio_mall = [0.2, 0.1, 0.7]

source_order_coldstart = ['featured', 'newpost', 'shop']
source_ratio_coldstart = [0.3, 0.5, 0.2]

source_order_manual_curating = ['newpost']
source_ratio_manual_curating = [1]

# Ads slot config
ads_hashtag_slot = 3
ads_search_slot = 2
ads_shop4you_slot = 2
ads_discovery_trending = 0.2
ads_discovery_4you = 0.2

discovery_4you_time_limit = 7
manual_curating_time_limit = 5
manual_select_keyword = ["đi biển", "đầm dây", "maxi", "Đầm hở lưng", "Áo hở lưng", "váy voan", "Đầm voan hoa", "chân váy voan", "đầm voan dây", "sơ mi họa tiết", "bikini", "áo dây", "sandal", "sandals", "đồ bơi", "tote", "bodysuit", "sơ mi caro", "so mi hoa", "somi", "áo dây", "áo dây linen", "áo dây hoa",
                         "Croptop hoa nhí", "Croptop caro", "Croptop", "caro", "váy caro", "đầm caro", "Đầm mini", "Đầm midi", "đầm hoa", "chân váy", "quần short", "quần đùi chất đũi", "set bộ", "Set thể thao", "Set sơ mi", "túi tote", "váy tennis", "váy tennis caro", "jean loe", "bangdo", "váy caro", "dép", "Dép xỏ", "sandal", "non", "nón"]

cold_start_threshold = 5
history_max_like_time = 10
history_min_like_time = 5
history_max_dislike_time = 1
history_min_dislike_time = 0
latest_history_threshold = 10
latest_history_expire_day = 30
avoid_history_trim_limit = 300
negative_post_penalty_coef = 0.2

score_boost_expire_day = 7
score_boost_use_seller_ranking_score = 0

keyword_list: list[str] = []
keyword_img_list: list[str] = []

keyword_hashtag_ids: list[int] = [14, 1638, 15863]

hashtag_sssmarket_tip_post = sorted([38508, 26805, 33168, 9451, 42492, 39171], reverse=True)
hashtag_manual_weight = 2
hashtag_likecount_weight = 0.5
hashtag_postcount_weight = 0.5
hashtag_timeframe_day_limit = 30
hashtag_postcount_threshold = 3

promotion_voucher_hour_limit = 24*14

similarity_cache_expire_hour = 168
similarity_score_threshold = 0.3
shoe_shop_similarity_filter = [36, 46, 187]
similarity_index_name = 'similarity_index_5'

# keyword_sss_suggestion = ['váy','áo khoác','cardigan','hoodie','sweater','gile','áo len','boot',
# 'bomber','croptop','túi','jeans','blazer','áo nỉ','khoác kaki','denim','khoác dạ','váy midi']
keyword_sss_suggestion = ['áo len', 'cardigan', 'croptop', 'boots', 'hoodie',
                          'jeans', 'sweater', 'túi', 'váy midi', 'váy']
keyword_sss_suggestion_url = {
    'áo len': 'media/icon/search_icons/ao-len.jpg',
    'cardigan': 'media/icon/search_icons/cardigan.jpg',
    'croptop': 'media/icon/search_icons/croptop.jpg',
    'boots': 'media/icon/search_icons/footwear.jpg',
    'hoodie': 'media/icon/search_icons/hoodie.jpg',
    'jeans': 'media/icon/search_icons/jeans.jpg',
    'sweater': 'media/icon/search_icons/sweater.jpg',
    'túi': 'media/icon/search_icons/tui.jpg',
    'váy midi': 'media/icon/search_icons/vay midi.jpg',
    'váy': 'media/icon/search_icons/vay.jpg',
}
faiss_cache_expire_hour = 12

cache_time_long = 3600*24
cache_time_medium = 3600*6
cache_time_short = 3600*1

time_limit_long = 30
time_limit_medium = 7
time_limit_short = 3

post_limit_big = 499
post_limit_medium = 199
post_limit_small = 199

offline_time_limit = 7
embed_post_size = 32
style_post_size = 11

leaderboard_size = 20

home_api_test_user = [3, 5, 513, 79460, 708, 91702, 154, 82, 85, 73355, 100006, 130381, 140322, 153899, 154824, 846587]

home_api_merchandise_user = [270971, 270975]

home_banner_feature_list = [
    'Xu',
    'Leaderboard',
]

home_api_different_random_cache_number = 10

home_api_text_utlity_carousel_voucher_screen = unicodedata.normalize('NFKC', 'Voucher')
home_api_text_utlity_carousel_leaderboard = unicodedata.normalize('NFKC', 'Xếp hạng')
home_api_text_utlity_carousel_discovery = unicodedata.normalize('NFKC', 'SSSFeeds')
home_api_text_utlity_carousel_coin = unicodedata.normalize('NFKC', 'Bonbon Xu')
home_api_text_utlity_carousel_ssslive = unicodedata.normalize('NFKC', 'SSSLive')
home_api_text_utlity_carousel_vf = unicodedata.normalize('NFKC', 'Phòng thử đồ')
home_api_text_utlity_carousel_ssstip = unicodedata.normalize('NFKC', 'SSSTips')
home_api_text_utlity_carousel_voucher = unicodedata.normalize('NFKC', 'Shop sales')
home_api_text_utlity_carousel_search = unicodedata.normalize('NFKC', 'Tìm đồ')

home_api_text_kol_header = unicodedata.normalize('NFKC', 'Tủ đồ của người nổi tiếng')
home_api_text_collection_banner_header = unicodedata.normalize('NFKC', 'Bộ sưu tập thời trang')

home_api_text_search_header = unicodedata.normalize('NFKC', 'Top tìm kiếm')

home_api_text_personalize_hashtag_header = unicodedata.normalize('NFKC', 'Trợ lí ảo Bonbon')
home_api_text_personalize_hashtag_recsys = unicodedata.normalize('NFKC', 'Hợp gu lại còn phong cách')
home_api_text_personalize_hashtag_male_item = unicodedata.normalize('NFKC', 'Đẹp trai hơn nhiều chút')
home_api_text_personalize_hashtag_nearby = unicodedata.normalize('NFKC', 'Ở đâu ship liền')
home_api_text_personalize_hashtag_follower = unicodedata.normalize('NFKC', 'Follower hôm nay có gì')

home_api_text_banner_header = unicodedata.normalize('NFKC', 'Thế giới thời trang')
home_api_text_banner_sssmarket_collection = unicodedata.normalize('NFKC', 'SSSMarket collection')
home_api_text_banner_sssmarket_collection_subtitle = unicodedata.normalize('NFKC', 'SSSMarket collection')
home_api_text_banner_luxury = unicodedata.normalize('NFKC', 'Hàng hiệu')
home_api_text_banner_luxury_subtitle = unicodedata.normalize('NFKC', 'Đồ thương hiệu chất lượng')
home_api_text_banner_sssmall = unicodedata.normalize('NFKC', 'SSSMall')
home_api_text_banner_sssmall_subtitle = unicodedata.normalize('NFKC', 'Shop được SSS đảm bảo')
home_api_text_banner_cheap = unicodedata.normalize('NFKC', 'Rẻ bất ngờ')
home_api_text_banner_cheap_subtitle = unicodedata.normalize('NFKC', 'Mua được vô số thứ chỉ với 50K')
home_api_text_banner_recent = unicodedata.normalize('NFKC', 'New arrival')
home_api_text_banner_recent_subtitle = unicodedata.normalize('NFKC', 'Sản phẩm mới đăng')

home_api_text_tab_frame_header = unicodedata.normalize('NFKC', 'Nhiều người yêu thích')
home_api_text_brand_tab_frame_header = unicodedata.normalize('NFKC', 'Brand yêu thích')
home_api_text_hashtag_header = unicodedata.normalize('NFKC', 'Xu hướng hashtag')
home_api_text_livestream_header = unicodedata.normalize('NFKC', 'Livestream 🎥')


home_api_text_merchandise_hashtag_header = unicodedata.normalize('NFKC', 'Dành cho SSS Merchandise')

home_api_text_t2_shop_header = unicodedata.normalize('NFKC', '🔥 Dọn tủ đồ đầu tuần 🔥')
home_api_text_t2_tabframe_header = unicodedata.normalize('NFKC', 'Dọn tủ đồ day - 21h-22h')
home_api_text_t3_tabframe_header = unicodedata.normalize('NFKC', 'SSSMall day 🛒 21h-22h')
# home_api_text_t4_shop_header=unicodedata.normalize('NFKC','🔥 Dọn tủ đồ đầu tuần 🔥')
home_api_text_t5_tabframe_header = unicodedata.normalize('NFKC', 'Săn hàng hiệu - 21h-22h')
home_api_text_flashsale_t6_hashtag_header = unicodedata.normalize('NFKC', '✨ Săn deal đồng giá ✨')
home_api_text_flashsale_t7_hashtag_header = unicodedata.normalize('NFKC', '🔥 Săn deal cuối tuần 🔥')
home_api_text_flashsale_t7_shop_header = unicodedata.normalize('NFKC', '🛒 Deal từ Shop 🔥')
home_api_text_t7_cn_tabframe_header = unicodedata.normalize('NFKC', 'SFashionn 🛒 21h-22h')

home_api_text_june_shop_week_2_header = unicodedata.normalize('NFKC', 'Local brand sale shock')

# Common Home component - with order as shown
home_common_components = [
    'event',
    'utility',
    'kol_banner',
    'feature_event',
    'tabframe',
    'livestream',
    'brand_tabframe',
    'collection_banner',
    'common_shop',
    'banner_hashtag',
    'hashtag',
    # 'discovery_event'
]

# Special event Home component - with order as shown
home_events_components = [
    'event',
    'utility',
    'kol_banner',
    'feature_event',
    'camp_tabframe_t2',
    'sssmall_tabframe_t3',
    'sfashionn_tabframe_t7_cn',
    'brand_tabframe',
    'tabframe',
    'livestream',
    'collection_banner',
    'common_shop',
    'banner_hashtag',
    'hashtag',
    # 'discovery_event'
]

home_seed_components = ['personalize_shop' if comp == 'common_shop' else comp for comp in home_common_components.copy()]


# # with order as shown
merchandise_components = [
    'merchandise_offline_shop',
    'merchandise_online_shop',
    'merchandise_hashtag'
]

# order from last to first, so will not break order when insert
home_merchandise_components = [
    ('personalize_hashtag', -1)
]

# order from last to first, so will not break order when insert
home_personalize_components = [
    ('personalize_hashtag', 2)
]

collection_config_june = {
    "y2k": {
        "id": "y2k",
        "text": "Y2K",
        "thumbnail": "media/collection/0722/Y2KCollection.jpg",
        "keywords": ["túi xách", "kính râm", "bucket", "bandana", "kẹp tóc", "cardigan", "quần jeans", "jeans ống loe", "corset", "tie dye", "crop top", "chân váy", "áo hai dây", "chân váy xếp li", "dây chuyền", "cargo", "túi kẹp nách", "Y2K", "boots"],
        "avoid_keywords": [],
        "curating_acc": []
    },
    "hiking": {
        "id": "hiking",
        "text": "Leo núi",
        "thumbnail": "media/collection/0722/HikingCollection.jpg",
        "keywords": ["balo", "snearker", "thể thao", "jogger", "short nam", "mũ tai bèo", "nón tai bèo", "bucket", "lưỡi trai", "bomber", "short jeans", "áo thun", "quần jeans", "khoác jeans", "giày thể thao", "legging", "quần biker", "kính mát", "nón kết", "áo thun", "croptop"],
        "avoid_keywords": [],
        "curating_acc": [{"id": 130381, "start": "8/6/2022", "end": None}]
    },
    "picnic": {
        "id": "picnic",
        "text": "Picnic",
        "thumbnail": "media/collection/0722/PicnicCollection.jpg",
        "keywords": ["sơ mi caro", "so mi hoa", "somi", "áo dây", "áo dây linen", "áo dây hoa", "croptop hoa nhí", "croptop caro", "croptop", "caro", "váy caro", "đầm caro", "đầm mini", "đầm midi", "đầm hoa", "chân váy", "quần short", "quần đùi chất đũi", "set bộ", "set thể thao", "set sơ mi", "túi tote", "váy tennis", "váy tennis caro", "jean loe", "bangdo", "váy caro", "dép", "dép xỏ", "sandal", "non", "nón"],
        "avoid_keywords": [],
        "curating_acc": [{"id": 130381, "start": "8/6/2022", "end": None}]
    },
    "sea": {
        "id": "sea",
        "text": "Đi biển",
        "thumbnail": "media/collection/0722/SeaCollection.jpg",
        "keywords": ["đi biển", "đầm dây", "maxi", "đầm hở lưng", "áo hở lưng", "váy voan", "đầm voan hoa", "chân váy voan", "đầm voan dây", "sơ mi họa tiết", "bikini", "áo dây", "sandal", "sandals", "đồ bơi", "tote", "bodysuit"],
        "avoid_keywords": [],
        "curating_acc": [{"id": 130381, "start": "8/6/2022", "end": None}]
    },
    "blazer": {
        "id": "blazer",
        "text": "Blazer",
        "thumbnail": "media/collection/0722/BlazerCollection.jpg",
        "keywords": ["blazer"],
        "avoid_keywords": [],
        "curating_acc": []
    },
    "warm": {
        "id": "warm",
        "text": "Outfit ấm áp",
        "thumbnail": "media/collection/0722/WarmCollection.jpg",
        "keywords": ["áo khoác", "áo len", "áo khoác dạ", "khoác dạ", "áo nỉ", "sweater", "hoodie", "bomber", "khoác nỉ", "nón len", "măng tô", "áo hoodie", "áo khoác da", "len", "gile", "cardigan", "noel", "áo tay dài", "jogger", "quần nỉ", "lông", "cổ lọ"],
        "avoid_keywords": [],
        "curating_acc": []
    },
    "shoes": {
        "id": "shoes",
        "text": "Giày chất",
        "thumbnail": "media/collection/0722/ShoesCollection.jpg",
        "keywords": ["boot", "boots", "sneaker", "loafer", "mary jane"],
        "avoid_keywords": [],
        "curating_acc": []
    },
    "accessories": {
        "id": "accessories",
        "text": "Phụ kiện xinh",
        "thumbnail": "media/collection/0722/AccessoriesCollection.jpg",
        "keywords": ["vớ", "tất", "khăn", "dây chuyền", "vòng cổ", "bông tai", "vòng tay", "nón len", "bucket", "beanie"],
        "avoid_keywords": ["khăn pandana", "khăn bandana", "áo quây"],
        "curating_acc": []
    }
}


tabframe_label = [
    {'label': 'Tất cả', 'icon': 'media/category/tat-ca.png'},
    {'label': 'Đồ 2hand', 'icon': 'media/category/2hand.png'},
    {'cat': 1, 'label': 'Áo', 'icon': 'media/category/ao.png'},
    {'cat': 4, 'label': 'Đầm', 'icon': 'media/category/dam.png'},
    {'cat': 3, 'label': 'Quần', 'icon': 'media/category/quan.png'},
    {'cat': 2, 'label': 'Chân váy', 'icon': 'media/category/chan-vay.png'},
    {'cat': 7, 'label': 'Phụ kiện', 'icon': 'media/category/phu-kien.png'},
    {'cat': 12, 'label': 'Giày', 'icon': 'media/category/giay.png'},
    {'cat': 11, 'label': 'Túi', 'icon': 'media/category/tui.png'},
    {'cat': 6, 'label': 'Set quần áo', 'icon': 'media/category/set-quan-ao.png'},
    {'cat': 10, 'label': 'Áo khoác', 'icon': 'media/category/ao-khoac.png'},
    {'cat': 9, 'label': 'Áo len', 'icon': 'media/category/ao-len.png'},
    {'cat': 5, 'label': 'Đồ thể thao', 'icon': 'media/category/do-the-thao.png'},
    {'cat': 8, 'label': 'Khác', 'icon': 'media/category/khac.png'},
]

tabframe_label_t2 = [
    # {'label': 'Tất cả', 'icon': 'media/category/tat-ca.png'},
    {'label': 'Đồ 2hand', 'icon': 'media/category/2hand.png'},
    {'cat': 1, 'label': 'Áo', 'icon': 'media/category/ao.png'},
    {'cat': 4, 'label': 'Đầm', 'icon': 'media/category/dam.png'},
    {'cat': 3, 'label': 'Quần', 'icon': 'media/category/quan.png'},
    {'cat': 2, 'label': 'Chân váy', 'icon': 'media/category/chan-vay.png'},
    {'cat': 7, 'label': 'Phụ kiện', 'icon': 'media/category/phu-kien.png'},
    {'cat': 12, 'label': 'Giày', 'icon': 'media/category/giay.png'},
    {'cat': 11, 'label': 'Túi', 'icon': 'media/category/tui.png'},
    {'cat': 6, 'label': 'Set quần áo', 'icon': 'media/category/set-quan-ao.png'},
    {'cat': 10, 'label': 'Áo khoác', 'icon': 'media/category/ao-khoac.png'},
    {'cat': 9, 'label': 'Áo len', 'icon': 'media/category/ao-len.png'},
    {'cat': 5, 'label': 'Đồ thể thao', 'icon': 'media/category/do-the-thao.png'},
    {'cat': 8, 'label': 'Khác', 'icon': 'media/category/khac.png'},
]

tabframe_label_sssmall = [
    {'label': 'Tất cả', 'icon': 'media/category/sssmall-logo-round.png'},
    # {'label':'Đồ 2hand', 'icon': 'media/category/2hand.png'},
    {'cat': 1, 'label': 'Áo', 'icon': 'media/category/ao.png'},
    {'cat': 4, 'label': 'Đầm', 'icon': 'media/category/dam.png'},
    {'cat': 3, 'label': 'Quần', 'icon': 'media/category/quan.png'},
    {'cat': 2, 'label': 'Chân váy', 'icon': 'media/category/chan-vay.png'},
    {'cat': 7, 'label': 'Phụ kiện', 'icon': 'media/category/phu-kien.png'},
    # {'cat':12, 'label': 'Giày', 'icon':'media/category/giay.png'},
    {'cat': 11, 'label': 'Túi', 'icon': 'media/category/tui.png'},
    {'cat': 6, 'label': 'Set quần áo', 'icon': 'media/category/set-quan-ao.png'},
    {'cat': 10, 'label': 'Áo khoác', 'icon': 'media/category/ao-khoac.png'},
    # {'cat':9, 'label': 'Áo len', 'icon':'media/category/ao-len.png'},
    # {'cat':5, 'label': 'Đồ thể thao', 'icon':'media/category/do-the-thao.png'},
    # {'cat':8, 'label': 'Khác', 'icon':'media/category/khac.png'},
]

tabframe_label_sfashionn = [
    {'label': 'Tất cả', 'icon': 'media/category/sfashionn-logo-round.png'},
    # {'label':'Đồ 2hand', 'icon':'media/category/2hand.png'},
    {'cat': 1, 'label': 'Áo', 'icon': 'media/category/ao.png'},
    {'cat': 4, 'label': 'Đầm', 'icon': 'media/category/dam.png'},
    {'cat': 3, 'label': 'Quần', 'icon': 'media/category/quan.png'},
    {'cat': 2, 'label': 'Chân váy', 'icon': 'media/category/chan-vay.png'},
    {'cat': 7, 'label': 'Phụ kiện', 'icon': 'media/category/phu-kien.png'},
    # {'cat':12, 'label': 'Giày', 'icon':'media/category/giay.png'},
    {'cat': 11, 'label': 'Túi', 'icon': 'media/category/tui.png'},
    {'cat': 6, 'label': 'Set quần áo', 'icon': 'media/category/set-quan-ao.png'},
    {'cat': 10, 'label': 'Áo khoác', 'icon': 'media/category/ao-khoac.png'},
    # {'cat':9, 'label': 'Áo len', 'icon':'media/category/ao-len.png'},
    # {'cat':5, 'label': 'Đồ thể thao', 'icon':'media/category/do-the-thao.png'},
    # {'cat':8, 'label': 'Khác', 'icon':'media/category/khac.png'},
]


leaderboard_titles = ['Shop', 'Bài đăng', 'Pass đồ Rinh xu']
shop_component_shop_post_lower_limit = 5

flashdeal_shops = []
flashsale_shops_t6 = []
flashsale_shops_t7_12h12 = []
flashsale_shops_t7_18h18 = []
flashsale_shops_t7_21h21 = []

eom_shop_ids = [335109, 310262, 362458, 89610, 400287, 390944, 105990, 266003, 354654, 132270, 281485, 220624, 314757, 320969, 303002, 545597, 387202, 341021, 372363, 351041, 115532, 272732,
                376614, 335864, 259711, 132686, 376434, 355447, 325935, 292018, 175604, 375081, 302436, 43904, 202839, 314357, 405193, 246891, 406447, 232140, 221660, 64939, 143889, 344563, 406071]

june_shop_week_2 = [597521, 603170, 599688, 599939, 603159, 603944, 604515, 600082, 611301]


DETECT_CLOTHING_LABELS_VN = {
    0: "Áo sơ mi",
    1: "Áo",
    2: "Áo sweater",
    3: "Áo len đan",
    4: "Áo khoác",
    5: "Vest",
    # 6: "quần dài",
    6: "Quần",
    7: "Quần ngắn",
    8: "Váy",
    9: "Áo khoác choàng",
    10: "Đầm",
    11: "Jumpsuit",
    12: "Kính mắt",
    13: "Mũ",
    14: "Phụ kiện đầu, tóc",
    15: "Đồng hồ",
    16: "Thắt lưng",
    17: "Giày",
    18: "Túi",
    19: "Khăn choàng"
}

DETECT_CLOTHING_LABELS_EN = {
    0: "shirt_blouse",
    1: "top_t-shirt_sweatshirt",
    2: "sweater",
    3: "cardigan",
    4: "jacket",
    5: "vest",
    6: "pants",
    7: "shorts",
    8: "skirt",
    9: "coat",
    10: "dress",
    11: "jumpsuit",
    12: "glasses",
    13: "hat",
    14: "headband_head-covering_hair-accessory",
    15: "watch",
    16: "belt",
    17: "shoe",
    18: "bag_wallet",
    19: "scarf"
}


model_gender = {
    1: 2,
    2: 1,
    3: 2,
    4: 1,
}

VF_POSITION_MAPPING = {
    # 0: other
    # 1: top
    # 2: bottom
    # 3: fullbody
    0: 1,
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 2,
    7: 2,
    8: 2,
    9: 1,
    10: 3
}


DB_DETECT_CATEGORY_ID_MAPPING = {
    1: [0, 1],                              # "ao": ["shirt, blouse", "top, t-shirt, sweatshirt"]
    2: [8],                                 # "chan-vay": ["Skirt"]
    3: [6, 7],                              # "quan": ["pants", "shorts"]
    4: [10],                                # "dam": ["Dress"]
    5: [1, 2, 4, 6],                    # "do-the-thao":
    6: [0, 1, 2, 3, 5, 6, 7, 8],        # "set-quan-ao":
    # "phu-kien" : ["glasses", "hat", "headband, head covering, hair accessory", "watch", "belt", "bag, wallet", "scarf"]
    9: [1, 2, 3, 6, 10],                # "do-len": ["top, t-shirt, sweatshirt", "sweater", "cardigan", "pants", "dress", "hat"]
    10: [2, 3, 4, 5, 9],                    # "ao-khoac-ngoai": ["sweater", "cardigan", "jacket", "vest", "coat"]
}

VF_DETECT_CATEGORY_ID_MAPPING = {
    0: 1,
    1: 1,
    2: 4,
    3: 4,
    4: 4,
    5: 1,
    # 6: 7,
    6: 6,
    7: 6,
    8: 8,
    9: 10,
    10: 10,
    11: 10,
    12: 10
}

VF_DETECT_CATEGORY_ID_MAPPING_PARALLEL = {
    0: [0, 1],
    1: [0, 1],
    2: [1],
    3: [1, 2, 3],
    4: [1, 3],
    5: [2, 3, 4],
    6: [7],
    7: [6],
    8: [8],
    9: [2, 3],
    10: [9, 10, 11]
}
