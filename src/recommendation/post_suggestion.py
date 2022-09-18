import numpy as np
from src.recommendation.new_watch_next import create_source_post
from src.recommendation.utils.recsys_scoring import get_user_vector_bytes, post_vec_query, _distance_score

def post_suggestion(user_id, reference_post_ids, source_order, pool_size=100):
    source_candidate_map = create_source_post(source_order, user_id, '', {})
    post_info_list = [pi for source in source_candidate_map for pi in source_candidate_map[source]][:pool_size]
    user_vector = np.frombuffer(get_user_vector_bytes(user_id), dtype=float).reshape(-1)
    candidate_post_vectors = [tup[1] for tup in post_vec_query([pi.pid for pi in post_info_list])]
    reference_post_vectors = [tup[1] for tup in post_vec_query(reference_post_ids)]
    result = {}
    for pi, candidate_vec in zip(post_info_list, candidate_post_vectors):
        min_distance = min([_distance_score(candidate_vec, reference_vec) for reference_vec in reference_post_vectors])
        result[pi.pid] = _distance_score(user_vector, candidate_vec) + min_distance

    return result


