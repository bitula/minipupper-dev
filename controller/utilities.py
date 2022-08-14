import os


def chk_rw_access(path, ro=False):     
    if os.path.exists(path):
        if not ro and (not os.access(path, os.R_OK) or not os.access(path, os.W_OK)):
            print("error: {0} has no read and/or write premission".format(path))
            return False
        elif ro and not os.access(path, os.R_OK):
            print("error: {0} has no read premission".format(path))
            return False
    else:
        print("fatal error: {0} not exported".format(path))
        return False
    
    return True


def chk_direction(path, direction="out"):
    with open(path, "r") as f:
        period = f.read()[:-1]
    if period != direction:
        return False
    
    return True