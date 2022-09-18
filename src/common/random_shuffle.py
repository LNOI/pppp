import numpy as np
from numpy.random import default_rng
from src.common.post_info_class import PostInfo
import logging
work_logger = logging.getLogger('work_logger')
err_logger = logging.getLogger('error_logger')

def random_shuffle(items, scores, p=1):
    if len(items) < 1 or len(scores) < 1:
        return items
    if len(items) != len(scores):
        raise Exception('Random shuffle input error: different len: %s vs %s' % (len(items), len(scores)))
    if p != 1:
        scores = [x**p for x in scores]
    np_scores = np.array(scores)
    # some regularize to reduce effect of score
    np_scores = np.add(np_scores, 0.2/len(np_scores))
    weight = np_scores/sum(np_scores)
    try:
        result_indexes = default_rng().choice(range(len(items)), size=len(items), replace=False, p=weight)
        # Avoid auto type convert in default_rng
        result_items = [items[i] for i in result_indexes]
    except ValueError as e:
        raise Exception('Random value error:') from e
    return list(result_items)

def random_post_info_shuffle(post_infos:list[PostInfo], p=1) -> list[PostInfo]:
    try:
        scores = [pi.post_score_info['score'] if 'score' in pi.post_score_info else pi.post_score_info['raw_score'] for pi in post_infos]
    except Exception as e:
        err_logger.error('PostInfo have neither score nor raw_score.', exc_info=True)
        scores = [1] * len(post_infos)
    result_post_infos = random_shuffle(post_infos, scores, p)
    return result_post_infos

def result_prob_random_change(post_infos:list[PostInfo], number:int) -> list[PostInfo]:
    if len(post_infos) < 1:
        work_logger.info('Recommend result prob change: len 0, no change')
        return post_infos
    selected_post_infos = random_post_info_shuffle(post_infos)[:number]
    work_logger.info('Recommend result prob change: selected with probability change: %s' % selected_post_infos)
    return selected_post_infos

