from src.utils.faiss_utils import sim_5_multi_search_index

import logging
deviation_logger = logging.getLogger('deviation_logger')
work_log = logging.getLogger('work_logger')

def query_similarity_5(post_id:int, number_of_post:int) -> list[int]:
    res = sim_5_multi_search_index(post_id, number_of_post)
    return res
