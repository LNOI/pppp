from src.utils.db_utils import execute_raw_query
import logging
work_logger = logging.getLogger('work_logger')
deviation_logger = logging.getLogger('deviation_logger')

def get_media_path(post_id:int) -> tuple[list[str], list[str]]:
    query = '''select m.file, m.mime_type from media m where m.post_id = :post_id order by m.id'''
    media_path_list = execute_raw_query(query, post_id=post_id)
    image_list = [item[0] for item in media_path_list if item[1]=='image']
    video_list = [item[0] for item in media_path_list if item[1]=='video']
    return image_list, video_list

def m_get_media_path(post_ids:list[int]) -> tuple[list[list[str]], list[list[str]]]:
    if len(post_ids) < 1:
        return [], []
    id_index_map = {pid:ix for ix,pid in enumerate(post_ids)}
    image_lists = [[] for i in range(len(post_ids))]
    video_lists = [[] for i in range(len(post_ids))]
    
    query = '''select m.file, m.mime_type, m.post_id from media m where m.post_id in :post_ids order by m.id'''
    media_path_list = execute_raw_query(query, post_ids=tuple(post_ids))
    for item in media_path_list:
        if item[1] == 'image':
            post_id = int(item[2])
            image_lists[id_index_map[post_id]].append(item[0])
        if item[1] == 'video':
            post_id = int(item[2])
            video_lists[id_index_map[post_id]].append(item[0])
    return image_lists, video_lists