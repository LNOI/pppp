import re
def remove_space(tag:str) -> str:
    tag = re.sub(r'\W+', '', tag)
    if tag == '':
        return ''
    return '#' + tag
def str_tag_to_list_tag(text:str) -> list[str]:
    result = []
    tags = text.split('#')
    for tag in tags:
        normalized_tag = remove_space(tag)
        if normalized_tag != '':
            result.append(normalized_tag)
    return result
def normalize_tag(text:str) -> str:
    hashtags = str_tag_to_list_tag(text)
    if len(hashtags) > 3:
        hashtags = hashtags[:3]
    return ' '.join(hashtags)

def id_str_to_id_list(idstr:str) -> list[int]:
    items = idstr.split(',')
    res = []
    for istr in items:
        try:
            res.append(int(istr))
        except Exception as e:
            pass
    return res