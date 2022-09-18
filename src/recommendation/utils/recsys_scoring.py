import math
import numpy as np
import scipy.spatial as spatial
from typing import List, Tuple, Dict
from src.const import const_map as CONST_MAP
from src.utils.query.user_history import get_latest_history
from src.common.get_style_history_vector import get_style_history_vector
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')

# Noti usage


def get_post_scores(candidate_post_tups: List[Tuple[int, np.ndarray]], user_liked_vector: List[np.ndarray], user_disliked_vector: List[np.ndarray]) -> Dict[int, float]:
    scores = []
    matched_results = []

    for i, (post_id, post_vector) in enumerate(candidate_post_tups):
        s = _score(user_liked_vector, user_disliked_vector, post_vector)
        scores.append(s)
        matched_results.append(post_id)
    return {k: v for k, v in zip(matched_results, scores)}


def _score(posts_liked: List[np.ndarray], posts_disliked: List[np.ndarray], content: np.ndarray) -> float:
    total_score = 0.0
    for post_liked in posts_liked:
        total_score += _distance_score(post_liked, content)
    for post_disliked in posts_disliked:
        total_score -= _distance_score(post_disliked, content)
    if (len(posts_liked) + len(posts_disliked)) > 0:
        mean_score = total_score / 0.00001 + len(posts_liked) + len(posts_disliked)
        return (mean_score + 1)
    else:
        return 1


def _distance_score(post_a: np.ndarray, post_b: np.ndarray) -> float:
    if CONST_MAP.score_func == 'norm':
        epsilon = 1.0
        score = 1 / (np.linalg.norm(post_a - post_b) + epsilon)
        if score is None or np.isnan(score):
            score = 1
    else:
        epsilon = 10e-5
        score = spatial.distance.cosine(post_a, post_b) + epsilon
        if score is None or np.isnan(score):
            score = epsilon
    return float(score)
# Scoring import


def post_vec_query(post_id_pool: list[int]) -> list[tuple[int, np.ndarray]]:
    post_recsys_vecs, _ = get_style_history_vector(list(post_id_pool), [])
    result_tup = []
    for pid, recsys_vec in zip(post_id_pool, post_recsys_vecs):
        result_tup.append((pid, recsys_vec))
    return result_tup


# Scoring import
# @redis_cache_value(lambda x: 'user_vector_with_meta:v2:id:%s' % x, expire_secs=1200)
def get_user_vector_bytes(user_id: int):
    liked_id, disliked_id, _, _ = get_latest_history(user_id)
    if len(liked_id) + len(disliked_id) < 1:
        return np.ones((CONST_MAP.embed_post_size,)).tobytes()
    work_logger.info('User: %s. Liked: %s' % (user_id, liked_id))
    work_logger.info('User: %s. Disliked: %s' % (user_id, disliked_id))
    posts_liked_vector, posts_disliked_vector = get_style_history_vector(liked_id, disliked_id)
    if len(posts_liked_vector) + len(posts_disliked_vector) < 1:
        return np.ones((CONST_MAP.embed_post_size,)).tobytes()
    total_liked_vector = posts_liked_vector
    total_disliked_vector = posts_disliked_vector
    total_score = len(total_liked_vector) + len(total_disliked_vector)
    vector_sum = np.zeros(CONST_MAP.embed_post_size)
    if len(total_liked_vector) > 0:
        vector_sum = vector_sum + np.sum(total_liked_vector, axis=0)
    if len(total_disliked_vector) > 0:
        vector_sum = vector_sum - np.sum(total_disliked_vector, axis=0)
    if total_score != 0:
        vector_sum = vector_sum / total_score
    return vector_sum.tobytes()

# Scoring import


def get_new_post_scores(candidate_post_tups: List[Tuple[int, np.ndarray]], user_vector: np.ndarray) -> Dict[int, float]:
    res = {}
    user_meta_vec = user_vector[:-CONST_MAP.style_post_size]
    user_style_vec = user_vector[-CONST_MAP.style_post_size:]
    user_gender_vec = user_meta_vec[1:6]
    user_cat_vec = user_meta_vec[6:]
    for (post_id, post_vector) in candidate_post_tups:

        meta_vec = post_vector[:-CONST_MAP.style_post_size]
        style_vec = post_vector[-CONST_MAP.style_post_size:]
        post_gender_vec = meta_vec[1:6]
        post_cat_vec = meta_vec[6:]
        # Score cua Quan lam
        price_score = cal_price_score(float(meta_vec[0]), float(user_meta_vec[0]))
        gender_score = cal_gender_score(post_gender_vec, user_gender_vec)
        category_score = cal_cat_score(post_cat_vec, user_cat_vec)
        style_score = cal_style_score(style_vec, user_style_vec)
        res[post_id] = price_score * 0.3 + gender_score * 0.2 + category_score * 0.1 + style_score * 0.4
        if res[post_id] <= 0:
            res[post_id] = 1e-4
    return res


def cal_price_score(post_price, user_price, upper: float = 0.25, lower: float = 0.45, base: float = 0.5, esp=1e-2):
    if (post_price > (user_price + user_price * upper)) | (post_price < (user_price - user_price * lower)):
        return esp
    else:
        if post_price < user_price:
            diff = (float(user_price - post_price)/(user_price - (user_price - user_price * lower)))**2
            return base + diff * (1 - base)
        else:
            diff = (float(user_price - post_price)/(user_price - (user_price + user_price * upper)))**2
            return base - diff * (1 - base)


def cal_gender_score(post_gender_vec: np.ndarray, user_gender_vec: np.ndarray) -> float:
    if np.all(post_gender_vec == 0.0):
        return 0.0
    user_norm_gender_vec = vec_standardize(user_gender_vec)
    idx = post_gender_vec.argmax()
    return user_norm_gender_vec[idx]


def cal_cat_score(post_cat_vec: np.ndarray, user_cat_vec: np.ndarray) -> float:
    if np.all(post_cat_vec == 0.0):
        return 0.0
    index_max_cat = post_cat_vec.argmax()
    user_norm_cat_vec = vec_standardize(user_cat_vec)
    return user_norm_cat_vec[index_max_cat]


def cal_style_score(post_style_vec: np.ndarray, user_style_vec: np.ndarray) -> float:
    d = 1 - spatial.distance.cosine(post_style_vec, user_style_vec)
    if math.isinf(d) or math.isnan(d) or d < 0:
        return 0.0
    return float(d)


def vec_standardize(vec: np.ndarray, esp=1e-8):
    vec = (vec-vec.min()) / (vec.max() - vec.min() + esp)
    return vec
