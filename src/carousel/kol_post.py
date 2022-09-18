from functools import partial
from src.common.source.kol_source import kol_post_source, order_by_recent_kol
from src.common.filter.post_sql_filter import gender, avoid_sold_post
from src.common.post_info_class import PostInfo


def kol_result(male_item=False) -> list[PostInfo]:
    filters = []
    # if male_item is True:
    #     filters.append(partial(gender, gender_ids=[1]))
    filters.append(partial(avoid_sold_post))
    filters.append(partial(order_by_recent_kol, male_item=male_item, interval_time='3 days'))
    total_pi = kol_post_source(filters)
    return total_pi
