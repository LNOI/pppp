from sqlalchemy.sql import text
from src.const.global_map import RESOURCE_MAP, CONFIG_SET
from src.utils.decorator import log_func_time
from typing import List, Tuple, Any

import logging
utils_logger = logging.getLogger('utils_logger')
deviation_logger = logging.getLogger('deviation_logger')

@log_func_time
def execute_raw_query(raw_query:str, **kwargs) -> List[Tuple[Any, ...]]:
    try:
        query = text(raw_query)
        rr = RESOURCE_MAP['db_engine'].execute(query, **kwargs).fetchall()
        res = [tuple(i) for i in rr]
        return res
    except Exception as e:
        if CONFIG_SET == 'prod':
            deviation_logger.error('Raw query failed: query %s: error: %s' % (raw_query, e), exc_info=True)
            return []
        else:
            deviation_logger.error('Raw query failed: query %s: error: %s' % (raw_query, e), exc_info=True)
            raise RuntimeError('SQL error') from e
