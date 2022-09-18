from src.utils.query.user_post import get_user_post_info
from src.const import const_map as CONST_MAP
from typing import List
from src.utils.decorator import log_func_time

@log_func_time
def dashboard_creation() -> List[int]:
    dashboard_account_results = get_user_post_info(CONST_MAP.dashboard_user_id, 
                                                    CONST_MAP.dashboard_post_day_limit, 
                                                    CONST_MAP.dashboard_post_limit, 
                                                    keep_sold=False)
    dashboard_results = dashboard_account_results + CONST_MAP.dashboard_post_id
    return dashboard_results