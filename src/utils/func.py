def dedup_with_order(collection, key_function=lambda x:x):
    res = []
    appeared_keys = []
    for item in collection:
        item_key = key_function(item)
        if item_key not in appeared_keys:
            res.append(item)
            appeared_keys.append(item_key)
    return res
