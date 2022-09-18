from src.utils.db_utils import execute_raw_query

def get_commitment_score():
    query = '''with cancel_events as (
    select order_id, oo.date, oo.user_id, (oo.parameters -> 'cancelled_by')::text as target
    from order_orderevent oo 
    where  oo.date > current_date - interval '1 month'
    and oo."type" = 'cancelled'
)
select user_id, count(*) + 1 as deduced 
from cancel_events
where target in ('"delivery_platform"', '"system"', '"seller"')
group by 1
'''
    res = execute_raw_query(query)
    special_score_map = {}
    for pid, score in res:
        special_score_map[pid] = score
    return special_score_map