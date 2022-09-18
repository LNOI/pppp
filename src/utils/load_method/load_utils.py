import sys
import logging

from typing import Any, Callable
from src.const import global_map


logger = logging.getLogger('utils_logger')


def register_load_method(func:Callable) -> Callable:
    if func.__name__ in global_map.METHOD_MAP:
        raise SyntaxError(f'Duplicate load method name: {func.__name__}')
    global_map.METHOD_MAP[func.__name__] = func
    return func

def load_single_resource(single_resource_name:str) -> Any:
    if 'fastapi_resource' not in sys.modules:
        import src.utils.load_method.fastapi_resource
    if 'common_resource' not in sys.modules:
        import src.utils.load_method.common_resource
    if 'model_resource' not in sys.modules:
        import src.utils.load_method.model_resource
    # Load one resource using required method and provided info
    single_resource_info = global_map.CONFIG_MAP['resource'][single_resource_name]
    resource = None
    load_method = global_map.METHOD_MAP[single_resource_info['method']]
    resource = load_method(**single_resource_info['args'])
    logger.info('{} loading success.'.format(single_resource_name))
    return resource

