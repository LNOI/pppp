import math
def post_score_modify(db_post_score:float, post_age:int, last_online:int, user_ordinal:int) -> float:
    modified_score = db_post_score * post_decay_coef(post_age) * online_score(last_online) * period_promoting(user_ordinal)
    # modified_score = db_post_score * period_promoting(user_ordinal)
    return modified_score

def online_score(seller_last_online_day):
    if seller_last_online_day > 7:
        return 1/math.log(seller_last_online_day, 7)
    return 1.0

def post_decay_coef(post_day_age):
    if post_day_age > 3:
        return 1/math.log(post_day_age, 3)
    return 1.0

def period_promoting(user_ordinal:int):
    if type(user_ordinal) is not int:
        return 0.0
    period = user_ordinal % 10
    if period not in [1, 5]:
        return 1.0
    if period == 5:
        return 1.5
    if period == 1:
        return 2.0
