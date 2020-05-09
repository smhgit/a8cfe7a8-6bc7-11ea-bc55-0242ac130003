'''General utils, not related specific to custom components'''

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False