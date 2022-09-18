from src.utils.db_utils import execute_raw_query
from src.chat_suggestion.buyer_suggestion import buyer_suggestion
from src.chat_suggestion.seller_suggestion import seller_suggestion

import logging
deviation_logger = logging.getLogger('deviation_logger')
def is_seller(user_id:int, post_id:int) -> bool:
    query = 'select user_id from post p where p.id = :post_id'
    try:
        res = execute_raw_query(query, post_id=post_id)[0][0]
        poster_id = int(res)
        if poster_id == user_id:
            return True
        return False
    except Exception as e:
        deviation_logger.error('Seller check error: Post %s: Error %s' % (post_id, e), exc_info=True)
        return False

def chat_suggestion(user_id:int, post_id:int) -> list[dict[str,str]]:
    if is_seller(user_id, post_id):
        return seller_suggestion()
    else:
        return buyer_suggestion(user_id)