from src.utils.db_utils import execute_raw_query

def get_sss_tip_post() -> list[int]:
    query_res = query_sss_tip_post()
    post_ids = [int(i) for i in query_res['post_ids']]
    return post_ids

def query_sss_tip_post() -> dict:
    query = '''
    select id
    from post p
    where note = 'ssstips'
    order by id desc 
    '''
    res = execute_raw_query(query)
    post_ids = [int(item[0]) for item in res]
    return {'post_ids':post_ids}