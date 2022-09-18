from src.carousel.watchnext_post import get_following_post_info, get_popular_post_info
from src.recommendation.source.recsys_source import new_recsys_today_index_source
from src.utils.exception import NotificationError

def personalize_content_for_notification(user_id:int) -> int:
    recsys_pis = new_recsys_today_index_source(user_id, limit=15)
    if len(recsys_pis) > 0:
        return [pi.pid for pi in recsys_pis][0]
    else:
        raise NotificationError('No satisfy recsys post to recommend personalize content.')


def following_post_notification(user_ids:list[int], hour_limit=72) -> dict[int, list[int]]:
    final_res = {}
    for user_id in user_ids:
        candidate_map = {'following': get_following_post_info(user_id, None)}
        final_res[user_id] = [pi.pid for pi in candidate_map['following']]
    return final_res

def popular_post_notification() -> list[int]:
    filter_args = {
        "user_id":-1,
        "category": [],
        "size": [],
        "condition": [],
        "sex": [],
        "price": []
    }
    popular_pis = get_popular_post_info(filter_args)
    popular_pids = [pi.pid for pi in popular_pis]
    return popular_pids