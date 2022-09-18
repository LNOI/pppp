from datetime import datetime
from src.const import const_map as CONST_MAP
from src.const.global_map import RESOURCE_MAP

def get_current_time() -> datetime:
    try:
        return datetime.strptime(str(CONST_MAP.request_time), '%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        return datetime.now()

def get_query_time_str() -> str:
    try:
        datetime.strptime(str(CONST_MAP.request_time), '%Y-%m-%dT%H:%M:%S')
        return f" to_timestamp('{CONST_MAP.request_time}', 'YYYY-MM-DDTHH:MI:SS')"
    except Exception as e:
        return " now()"