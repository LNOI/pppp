def add_order_top_posts(query:str, order_cols:list[str]=None, direction:list[str]=None) -> str:
    if order_cols is None and direction is None:
        return query + '''
        order by id in (select id from top_posts tp order by tp.score) desc
        '''
    else:
        if direction is None:
            zip_col = zip(order_cols, ['asc'] * len(order_cols))
        else:
            zip_col = zip(order_cols, direction)

        query = query + '''
        order by id in (select id from top_posts tp order by tp.score) desc, %s
        ''' % ','.join([' %s %s ' % (col, d) for col, d in zip_col])
        return query


def add_order(query:str, order_cols:list[str], direction:list[str]=None) -> str:
    if direction is None:
        zip_col = zip(order_cols, ['asc'] * len(order_cols))
    else:
        zip_col = zip(order_cols, direction)
    return query + '''
    order by %s ''' % ','.join([' %s %s ' % (col, d) for col, d in zip_col])


def add_row_limit(query:str, limit:int) -> str:
    return query + '''
    limit %s''' % int(limit)