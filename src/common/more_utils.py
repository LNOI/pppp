import math
from typing import Any
from src.common.post_info_class import PostInfo
from src.utils.db_utils import execute_raw_query

def get_user_gender_id(user_id):
    query = '''select au.gender from account_user au where au.id = :user_id'''
    res = execute_raw_query(query, user_id=user_id)
    if 0 < int(res[0][0]) < 4:
        return int(res[0][0])
    else:
        return 2

def get_user_address(user_id, address_level = 1):
    address = 'concat(aa.province' 
    if address_level == 2:
        address = address + ', \'_\', aa.district'
    if address_level == 3:
        address = address + ', \'_\', aa.ward'
    address = address + ')'
    query = '''select %s from account_user au join account_address aa on au.default_address_id = aa.id where au.id = :user_id ''' % (address)
    res = execute_raw_query(query, user_id=user_id)
    if len(res) > 0:
        return str(res[0][0])
    else:
        return ''

def split_post_infos_by_user(post_infos:list[PostInfo]) -> dict[int, list[PostInfo]]:
    # Assume all post infos already contain user id in source_specific_info attribute
    shop_pi_map = {}
    for pi in post_infos:
        if pi.source_specific_info['user_id'] not in shop_pi_map:
            shop_pi_map[pi.source_specific_info['user_id']] = [pi]
        else:
            shop_pi_map[pi.source_specific_info['user_id']].append(pi)
    return shop_pi_map

def order_selection(itemss:list[list[Any]], ratios:list[float], total_required:int):
    required_numbers = [math.ceil(ratio*total_required) for ratio in ratios]
    selected_itemss = [items[:required] for items, required in zip(itemss, required_numbers)]
    current_number = sum([len(i) for i in selected_itemss])
    if current_number < total_required:
        for i in range(len(itemss)):
            if len(itemss[i][required_numbers[i]:]) > 0:
                if current_number + len(itemss[i][required_numbers[i]:]) < total_required:
                    selected_itemss[i] = selected_itemss[i] + itemss[i][required_numbers[i]:]
                    current_number += len(itemss[i][required_numbers[i]:])
                else:
                    remain_required = total_required - current_number
                    selected_itemss[i] = selected_itemss[i] + itemss[i][required_numbers[i]:(required_numbers[i]+remain_required)]
                    break
    return selected_itemss
