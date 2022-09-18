import unicodedata

# from top sellers
def from_top_seller(query:str) -> str:
    return query + '''
    and (user_id in (select id from top_sellers)) '''

# item posted within x days
def new_arrival(query:str, days) -> str:
    return query + ''' 
    and p.created_at > now() - interval ' %s days' ''' % int(days)

# is secondhand
def secondhand(query:str) -> str:
    return query + '''
    and (p.ai_metadata -> '2hand')::boolean = True '''


# is new // is_stock_available la hang order
def newitem(query:str) -> str:
    return query + '''
    and (p.is_stock_available = false or condition_id = 5) '''


# price (post.amount) is less than x
def pricing_less(query:str, amount) -> str:
    return query + '''
    and p.amount is not null and p.amount <= %d''' % float(amount)

# price (post.amount) is more than x
def pricing_more(query:str, amount) -> str:
    return query + '''
    and p.amount is not null and p.amount >= %d''' % float(amount)

# price (post.amount) is from x to y
def pricing_inrange(query:str, amount_min, amount_max) -> str:
    return query + '''
    and p.amount is not null and p.amount between %d and %d''' % (float(amount_min), float(amount_max))

# brand is not null or other (khác)
def have_brand(query:str) -> str:
    return query + '''
    and (p.brand is not null and replace(regexp_replace(lower(p.brand), '[^\w]+',''), ' ', '') in (
    select replace(regexp_replace(lower(name), '[^\w]+',''), ' ', '')
    from brand
    where regexp_replace(lower(name), '[^\w]+','') != 'khác'
) ) '''

# gender filter
def gender(query:str, gender_ids:list[int]) -> str:
    if len(gender_ids) > 0:
        query += '''
    and p.gender_id in (%s)''' % ','.join([str(g) for g in gender_ids])
    return query

# from curator account
def curating(query:str, account_level_id:int) -> str:
    return query + '''
    and p.account_level_id = %s''' % str(account_level_id)

# from designed accounts (level)
def account_level(query:str, account_level_ids) -> str:
    return query + '''
    and p.account_level_id in (%s)''' % str(account_level_ids)

# biz account
def is_business_acc(query:str) -> str:
    return query + '''
    and p.is_business_acc is true
    '''

# geo-ly nearby
def is_nearby(query:str, user_address) -> str:
    query = query + '''
    and concat(p.province, '_', p.district, '_', p.ward) like %s
    ''' % f"'%{user_address}%'"
    return query

# category filter
def in_category(query:str, categories:list[int]) -> str:
    if None in categories:
        query += '''
    and p.category_id is null '''
    
    non_null_categories = [cat for cat in categories if cat is not None]
    if len(non_null_categories) > 0:
        query += '''
    and p.category_id in (%s)''' % ','.join([str(i) for i in non_null_categories])
    return query

# category filter
def avoid_category(query:str, categories:list[int]) -> str:
    if None in categories:
        query += '''
    and p.category_id is not null '''
    
    non_null_categories = [cat for cat in categories if cat is not None]
    if len(non_null_categories) > 0:
        query += '''
    and p.category_id not in (%s)''' % ','.join([str(i) for i in non_null_categories])
    return query

# size filter
def in_size(query:str, sizes:list[int]) -> str:
    if len(sizes) > 0:
        query += '''
    and p.size_id in (%s)''' % ','.join([str(i) for i in sizes])
    return query

# condition (clothing) filter
def in_condition(query:str, conditions:list[int]) -> str:
    if len(conditions) > 0:
        query += '''
    and p.condition_id in (%s)''' % ','.join([str(i) for i in conditions])
    return query

# ???
def in_watchnext_price(query:str, prices:list[int], feature_user_ids:list[int]) -> str:
    if len(prices) == 2:
        if len(feature_user_ids) < 1:
            feature_user_ids = [-1]
        query += '''
    and ((p.amount >= %s and p.amount <= %s) or p.user_id in (%s))''' % (prices[0], prices[1], ','.join([str(i) for i in feature_user_ids]))
    return query

# user_id filter
def belong_to_user(query:str, user_ids:list[int]) -> str:
    if len(user_ids) > 0:
        query += '''
    and p.user_id in (%s)''' % ','.join([str(i) for i in user_ids])
    return query

# user_id filter
def avoid_user(query:str, user_ids:list[int]) -> str:
    if len(user_ids) > 0:
        query += '''
    and p.user_id not in (%s)''' % ','.join([str(i) for i in user_ids])
    return query

# not showing sold posts
def avoid_sold_post(query:str) -> str:
    query += '''
    and p.is_sold = false and p.is_for_sale = true'''
    return query

# not showing reported post
def avoid_banned_post(query:str, user_id:int) -> str:
    query += f'''and p.id not in (
select CAST (rl.object_id as int)
from reporting_log rl
where rl.reported_by_id = {user_id}
and rl.object_type_id = 17
) and
p.user_id not in (
select CAST (rl.object_id as int)
from reporting_log rl
where rl.reported_by_id = {user_id}
and rl.object_type_id = 6)
and p.user_id not in (
select b.user_id
from blocking b
where b.blocked_by = {user_id})
    '''
    return query

# number of views filter
def total_view_greater(query:str, limit:int) -> str:
    query += f'''
    and p.total_views <= {limit}'''
    return query

# checking ai-metadata exist
def metadata_exist(query:str) -> str:
    query += '''
    and ai_metadata is not null
    and ai_metadata != '{}' '''
    return query

# id filtering
def in_candidate(query, candidates:list[int]) -> str:
    if len(candidates) > 0:
        query += f'''
        and p.id in (%s) ''' % ','.join([str(i) for i in candidates])
    else:
        query += '''
        and false '''
    return query

# video
def have_video_thumbnail(query:str) -> str:
    return query + '''
    and p.thumbnail like '%.gif'
    '''

# keyword filter
def have_any_keyword(query:str, keywords:list[str]) -> str:
    if len(keywords) < 1 or len([i for i in keywords if len(i)>0]) < 1:
        return query
    norm_keyword = [unicodedata.normalize('NFKC', k).lower() for k in keywords]
    return query + '''
    and lower(normalize(p.caption, NFKC)) similar to '%%(%s)%%'
    ''' % '|'.join(norm_keyword)

# keyword filter
def avoid_keyword(query:str, keywords:list[str]) -> str:
    if len(keywords) < 1 or len([i for i in keywords if len(i)>0]) < 1:
        return query
    norm_keyword = [unicodedata.normalize('NFKC', k).lower() for k in keywords]
    return query + '''
    and lower(p.caption) not similar to '%%(%s)%%'
    ''' % '|'.join(norm_keyword)

# selling post
def is_for_sale(query:str, for_sale:bool) -> str:
    return query + '''
    and p.is_for_sale = %s
    ''' % for_sale