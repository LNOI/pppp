from src.utils.db_utils import execute_raw_query

def filter_2hand(post_ids:list[int]) -> list[int]:
    if len(post_ids) < 1:
        return []
    query = '''with post_tags as (
    select hp.post_id, string_agg(h.tag, ',') as hashtags
    from hashtag_post hp 
    left join hashtag h on hp.hashtag_id = h.id
    where hp.post_id in :post_ids
    group by 1
)
select pt.post_id, pt.hashtags, p.condition_id, p.caption
from post_tags pt
left join post p on p.id = pt.post_id'''
    res = execute_raw_query(query, post_ids=tuple(post_ids))
    accepted_post_ids = []
    for post_id, hashtags, condition_id, caption in res:
        if check_2hand(hashtags, condition_id, caption):
            accepted_post_ids.append(post_id)
    return [pid for pid in post_ids if pid in accepted_post_ids]

def check_2hand(hashtags, condition_id, caption):
    if condition_id is not None and condition_id < 5:
        return True
    if check_keywords_in_text(['thanh lý', '2hand'], hashtags):
        return True
    if check_keywords_in_text(['thanh lý', '2hand', 'pass', 'mặc 1l'], caption):
        return True
    return False

def check_keywords_in_text(keywords, text):
    text = text.lower().replace(' ', '')
    for keyword in keywords:
        if keyword.replace(' ', '') in text:
            return True
    return False
