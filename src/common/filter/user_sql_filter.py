
def is_business_acc(query):
    return query + '''
    and es.is_business_acc is true'''

def female_acc(query):
    return query + '''
    and es.gender in (2,3)'''

def male_acc(query):
    return query + '''
    and es.gender in (1)'''