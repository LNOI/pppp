import pickle
import json
from typing import Any, List, Dict
from src.utils.load_method.load_utils import register_load_method


@register_load_method
def load_pickle_object(file_path:str) -> Any:
    with open(file_path, 'rb') as f:
        return pickle.load(f)


@register_load_method
def load_json(file_path:str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)


@register_load_method
def load_txt_list(file_path:str) -> List[str]:
    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    content_list = [line.replace('\n', '') for line in lines]
    return content_list


@register_load_method
def load_whole_text_file(file_path:str) -> str:
    with open(file_path, 'r', encoding='UTF-8') as f:
        text = f.read()
    return text


@register_load_method
def create_config_obj(**kwargs) -> Dict[str,Any]:
    return dict(**kwargs)
