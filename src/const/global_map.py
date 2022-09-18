from typing import Dict, Any, Callable

CONFIG_MAP:Dict[str, Dict[str, Any]] = {}
RESOURCE_MAP:Dict[str, Any] = {}
METHOD_MAP:Dict[str, Callable] = {}
HOME_COMPONENT_MAP:Dict[str, Callable] = {}
CONFIG_SET = 'dev'