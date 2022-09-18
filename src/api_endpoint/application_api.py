import logging

from fastapi.requests import Request
from src.recommendation.source.recsys_source import new_recsys_today_index_source
from src.recommendation.post_suggestion import post_suggestion
from src.recommendation.source.recsys_source import multi_post_similar_source
from src.popular.get_popular import get_keyword_suggestion, get_keyword_suggestion_v2
from src.popular.solr_search import search_keyword
from src.popular.hashtag_suggestion import get_hashtag_suggestion, get_hashtag_suggestion_v2
from src.popular.get_popular import get_popular_hashtag_v2, get_popular_keyword_v2
from src.leaderboard.get_leaderboard_post import get_leaderboard_result
from src.chat_suggestion.suggestion import chat_suggestion
from src.utils.decorator import  anonymous_user
from src.utils.redis_utils import insert_to_set_key
from src.utils.faiss_utils import delete_id
from src.img_similarity.query_similarity import query_similarity_5
from src.api_endpoint.add_api import api_log, api_log_no_response_content, short_api_log
from src.utils.basemodel.response_schemas import create_response
from src.const.global_map import RESOURCE_MAP
from src.utils.basemodel import application_schemas as schemas


app = RESOURCE_MAP['fastapi_app']

logger = logging.getLogger('app_logger')
deviation_logger = logging.getLogger('deviation_logger')
err_logger = logging.getLogger('error_logger')


@app.post('/post_encoding')
@short_api_log
async def encoding(input_map: schemas.EncodingSchema ):
    post_ids = input_map.item
    res: dict[str, list[int]] = {
        'success_encode': [],
        'failed_encode': []
    }

    for post_id in post_ids:
        if type(post_id) == int and post_id > 0:
            insert_to_set_key('set_encode_queue:resize',
                              value=post_id, expire=-1)
            insert_to_set_key('set_encode_queue:similarity_5',
                              value=post_id, expire=-1)
            res['success_encode'].append(post_id)
        else:
            res['failed_encode'].append(post_id)
    return create_response(status=200, content= res)


@app.post('/user_update')
@short_api_log
async def user_update_api(input_map: schemas.SimpleUserSchema ):
    user_id = input_map.user_id
    insert_to_set_key('set_queue:user_update', value=user_id, expire=-1)
    return create_response(status=200, content="Ok")


@app.post('/popular_keyword')
@short_api_log
async def get_popular_keyword_api_v2(input_map: schemas.PopularKeywordSchema):
    number_of_keyword = input_map.number_of_keyword
    result = get_popular_keyword_v2(number_of_keyword)
    return create_response(status=200, content= result[:number_of_keyword])


@app.post('/popular_hashtag_v2')
@short_api_log
async def get_popular_hashtag_api_v2(input_map: schemas.PopularHashtagSchema):
    number_of_hashtag = input_map.number_of_hashtag
    result = get_popular_hashtag_v2(number_of_hashtag)
    return create_response(status=200, content=result[:number_of_hashtag] )


@app.post('/hashtag_suggestion')
@short_api_log
async def get_hashtag_suggestion_api(input_map: schemas.HashtagSuggestionSchema):
    user_id = input_map.user_id
    number_of_hashtag = int(input_map['number_of_hashtag'])
    res = get_hashtag_suggestion(user_id, number_of_hashtag)
    return create_response(status=200, content=res)


@app.post('/hashtag_suggestion_v2')
@short_api_log
async def get_hashtag_suggestion_api_v2(input_map: schemas.HashtagSuggestionSchema):

    user_id = input_map.user_id
    number_of_hashtag = input_map.number_of_hashtag
    res = get_hashtag_suggestion_v2(user_id, number_of_hashtag)
    return create_response(status=200, content=res)


@app.post('/delete_post_cache')
@short_api_log
async def delete_faiss_id(input_map: schemas.DeleleFaissSchema):
    
    post_ids = input_map.post_ids
    for post_id in post_ids:
        post_id = int(post_id)
        delete_id(post_id, 'faiss_index_v2')
        delete_id(post_id, 'buyable_faiss_index_v2')
        delete_id(post_id, 'similarity_index_5')
    return create_response(status=200, content="OK")


def get_similar_post_placeholder():
    return []


@app.post('/similar_post')
@short_api_log
async def get_similar_post(input_map: schemas.ImageSimilaritySchema):
    post_id = input_map.post_id
    number_of_post = input_map.number_of_post

    res = query_similarity_5(post_id, number_of_post)
    all_recommendation = [int(post_id) for post_id in res]
    if len(all_recommendation) == 0:
        logger.info('Img similarity post number = 0. Return empty list')
        return create_response(status=200, content=[])
    
    return create_response( status=200 ,content=all_recommendation)   


@app.post('/chat_suggestion')
@short_api_log
async def chat_suggest(input_map: schemas.ChatSuggestionSchema):
    user_id = input_map.user_id
    post_id = input_map.post_id
    res = chat_suggestion(user_id, post_id)
    return create_response(status=200, content=res)


@app.post('/leaderboard')
@short_api_log
async def leaderboard_api(input_map: schemas.LeaderboardSchema):

    res = get_leaderboard_result(input_map.user_id)
    return create_response(status=200, content=res)


@app.post('/post_suggestion')
@short_api_log
async def post_suggestion_api(input_map: schemas.PostSuggestionSchema):
    user_id = input_map.user_id
    reference_post_ids = input_map.reference_post_ids
    source_order = ['newpost']
    if 'source_name' in input_map:
        source_order = [input_map.source_name]
    pool_size = 100
    if 'pool_size' in input_map:
        pool_size = input_map.pool_size 
    res = post_suggestion(user_id, reference_post_ids, source_order, pool_size)
    return create_response(status=200, content=res)


@app.post('/post_suggest_for_user')
@short_api_log
async def recsys_source_api(input_map: schemas.PostSuggestUserSchema):
    user_id = input_map.user_id
    post_id = input_map.post_id
    post_infos = new_recsys_today_index_source(user_id)
    pids = [pi.pid for pi in post_infos]
    return create_response(status=200, content=pids)


@app.post('/keyword_search')
@short_api_log
async def keyword_search_api(input_map: schemas.WatchnextSchema):
    user_id = input_map.user_id
    keyword = input_map.keyword
    filter_args = {
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }
    if 'filter' in input_map:
        if 'category' in input_map.filter:
            filter_args['category'] = input_map.filter.category
        if 'size' in input_map.filter:
            filter_args['size'] = input_map.filter.size
        if 'condition' in input_map.filter:
            filter_args['condition'] = input_map.filter.condition
        if 'price' in input_map.filter and len(input_map.filter.price) == 2:
            filter_args['price'] = [int(i*10000)
                                    for i in input_map.filter.price]
        if 'sex' in input_map.filter:
            filter_args['sex'] = input_map.filter.sex
    res = search_keyword(user_id, keyword, filter_args)
    return create_response(status=200, content=res)


@app.post('/keyword_suggestion')
@short_api_log
async def keyword_suggestion_api(input_map: schemas.KeywordSuggestionSchema):
    user_id = input_map.user_id
    user_id = anonymous_user(user_id) 
    number_of_keyword = input_map.number_of_keyword
    res = get_keyword_suggestion(user_id, number_of_keyword)
    return create_response(status=200, content=res)


@app.post('/keyword_suggestion_v2')
@short_api_log
async def keyword_suggestion_v2_api(input_map: schemas.KeywordSuggestionSchema):
    user_id = input_map.user_id
    user_id = anonymous_user(user_id) 
    number_of_keyword = input_map.number_of_keyword
    res = get_keyword_suggestion_v2(user_id, number_of_keyword)
    return create_response(status=200, content=res)




@app.post('/item_commision_fee')
@short_api_log
async def item_commission_fee_api():
    res = {
        'commission_fee': 0,
        'commission_rate': 0
    }
    return create_response(status=200, content=res)


@app.post('/test_new')
@short_api_log
async def test_new(request:Request):
    input_map = request._json
    post_ids = input_map['post_ids']
    res_post_ids = multi_post_similar_source(post_ids)
    return create_response(status=200, content=res_post_ids)


@app.post('/andy_test')
@short_api_log
async def andy_test(request: Request):
    input_map = request._json
    result_str = input_map['user_id'] + ' - ' + input_map['post_id']
    resp = {
        "result": result_str
    }
    return create_response(status=200, content= resp)
