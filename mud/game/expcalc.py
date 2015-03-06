def expFor(level):
    if level == 0:
        return 0 #  base case
    elif level == 1:
        return 100 # arbitrary base exp
    else:
        factor = 1.2 #arbitrary factor
        return int((expFor(level-1)-expFor(level-2))*factor + expFor(level-1))
