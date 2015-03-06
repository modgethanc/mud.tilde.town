cached = [0,100] #base case, arbitrary level 1 base exp

def expFor(level):
    if len(cached)-1 >= level:
        return cached[level]
    else:
        factor = 1.2 #arbitrary factor
        cached.append(int((expFor(level-1)-expFor(level-2))*factor + expFor(level-1)))
        return cached[level]
