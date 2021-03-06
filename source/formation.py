from numpy import array, array_equal,ones,arange,zeros,amax
from itertools import product as iterprod

def buildorder(formation):
    """ Determine bounds of formation """
    minx = formation[0][0]
    maxx = formation[0][0]
    miny = formation[0][1]
    maxy = formation[0][1]
    for x,y in formation:
        if minx > x:
            minx = x
        elif maxx < x:
            maxx = x
        if miny > y:
            miny = y
        elif maxy < y:
            maxy = y

    """ Create Required Arrays """
    """ Both arrays are 2 larger than te formation requires"""
    field = ones((maxx - minx + 3, maxy - miny + 3))
    form = zeros((maxx - minx + 3, maxy - miny + 3))
    fmaxx, fmaxy = field.shape

    """ Filling array with truth values according to formation """
    for x,y in map(lambda x: x - array([minx - 1,miny - 1]), formation):
        form[x,y] = 1

    form = form == 1

    """ Paint-like fill operation on 0,0, sets them at 0 """
    field = fill(field, form)

    """ Will perform a reduction operation on each square with value of target"""
    """ It will add 1 to the square if all it's neighbors also have the value of target"""
    """ This results in a height/distance-from-border map type situation"""
    target = 0
    while target != amax(field):
        target += 1
        field = reduce(field, target)
    
    m = amax(field)

    outformation = []

    """ Recreates formation as a tuple of coordinates and the height/distance"""
    for i in iterprod(arange(0,field.shape[0]),arange(0,field.shape[1])):
        if form[i]:
            outformation.append((m - field[i],array(i)))

    """ Sorts the order based on lexicographical ordering and height/distance"""
    outformation = sorted(outformation, key=lambda x: x[1][0] + x[1][1]*fmaxx + x[0]*fmaxx*fmaxy)

    """ Restore Origin"""
    return [(x[0], x[1] + array([minx -1, miny -1])) for x in outformation]

def printbuildorder(formation):
    minx = formation[0][0]
    maxx = formation[0][0]
    miny = formation[0][1]
    maxy = formation[0][1]
    for x,y in formation:
        if minx > x:
            minx = x
        elif maxx < x:
            maxx = x
        if miny > y:
            miny = y
        elif maxy < y:
            maxy = y

    order = zeros((maxx - minx + 3, maxy - miny + 3))

    i = 1
    for x,y in map(lambda x: x - array([minx - 1,miny - 1]), formation):
        order[x,y] = i
        i += 1

    print(order)

def reduce(field,target):
    outfield = field.copy()
    maxx, maxy = field.shape
    
    for i in iterprod(arange(0,maxx),arange(0,maxy)):
        if field[i] == target:
            if identical_neighbours(field,i):
                outfield[i] += 1
                
    return outfield
            
def identical_neighbours(field,i):
    x,y = i
    maxx, maxy = field.shape
    t = field[x,y]
    
    if x != (maxx - 1):
        if field[x+1,y] != t:
            return False
    if y != (maxy -1):
        if field[x,y+1] != t:
            return False
    if x != 0:
        if field[x-1,y] != t:
            return False
    if y != 0:
        if  field[x,y-1] != t:
            return False

    return True

def fill(field, form):
    o = [(0,0)]
    maxx, maxy = field.shape

    while len(o) > 0:
        x,y = o.pop()
        if not form[x,y]:
            field[x,y] = 0
            for xn,yn in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]:
                if not (xn < 0 or xn >= maxx or yn < 0 or yn >= maxy):
                    if field[xn,yn] == 1:
                        o.append((xn,yn))

    return field
        

