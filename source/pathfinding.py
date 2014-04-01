from numpy import array, array_equal

class Step(object):
    def __init__(self, position, utility, order):
        self.pos = position
        self.util = utility
        self.ord = order

    def __str__(self):
        return "<" + str(self.pos) + ", util=" +str(self.util) + ", ord=" + str(self.ord) + ">"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return array_equal(self.pos, other.pos)

    def __hash__(self):
        return hash(str(self.pos))

    def __ne__(self,other):
        return self != other

    def __lt__(self,other):
        return self.util < other.util

    def __gt__(self,other):
        return self.util > other.util
    
##def findpathtoclosest(start, goal, obstacles):
##    bounds = getbounds(obstacles, goal)
##    start = Step(start, distance(start, goal), 0)
##    goal = Step(goal, None, None)
##    steps = [start]
##    i = 0
##    while i < len(steps) and g not in steps: 
##        for x in possiblesteps(steps[i],goal,obstacles, bounds):
##            if x not in steps:
##                steps.append(x)
##        i += 1
##
##    print(i)
##    if goal in steps:
##        return (True, extractpath(goal, steps))
##    else:
##        return (False, extractpath(min(steps),steps))
##
def findpathtoclosest(start, goal, obstacles):
    bounds = getbounds(obstacles, goal)
    start = Step(start, distance(start, goal), 0)
    goal = Step(goal, None, None)
    steps = {start}
    openable = {start}
    i = 0
    
    while len(openable) > 0 and g not in steps:
        i += 1
        o = min(openable)
        openable.remove(o)
        for x in possiblesteps(o, goal, obstacles, bounds):
            if x not in steps:
                steps.add(x)
                openable.add(x)

    print(i)
    if goal in steps:
        return (True, extractpath(goal, steps))
    else:
        return (False, extractpath(min(steps),steps))

def extractpath(goal, steps):
    for s in steps:
        if s == goal:
            current = s
            break
    path = [current]
    less_order = lambda x: x.ord == (current.ord - 1)
    is_adjacent = lambda x: distance(current.pos,x.pos) == 1.0
    condition = lambda x: less_order(x) and is_adjacent(x)
    while current.ord > 0:
        current = filter(condition, steps).__next__()
        path.append(current)

    path.reverse()
    return [ x.pos for x in path[1:]]
        

def getbounds(obstacles, goal):
    minx = obstacles[0][0]
    maxx = obstacles[0][0]
    miny = obstacles[0][1]
    maxy = obstacles[0][1]
    for x,y in obstacles:
        if minx > x:
            minx = x
        elif maxx < x:
            maxx = x
        if miny > y:
            miny = y
        elif maxy < y:
            maxy = y

    x,y = goal
    if minx > x:
        minx = x
    elif maxx < x:
        maxx = x
    if miny > y:
        miny = y
    elif maxy < y:
        maxy = y    
    
    return (minx - 1, maxx + 1, miny - 1, maxy + 1)

def possiblesteps(point, goal, obstacles, bounds):
    within_bounds = lambda p: p[0] >= bounds[0] and p[0] <= bounds[1] and p[1] >= bounds[2] and p[1] <= bounds[3]
    is_free = lambda x: not any(map(lambda y: array_equal(x,y),obstacles)) and within_bounds(x)
    make_step = lambda x: Step(x, distance(x,goal.pos), point.ord + 1)
    return list(map(make_step, filter(is_free, [point.pos + array([1,0]),
                                 point.pos + array([0,1]),
                                 point.pos + array([-1,0]),
                                 point.pos + array([0,-1])])))

def distance(p, q):
        return pow(pow(p[0]- q[0],2) + pow(p[1]- q[1],2), 0.5)


start = array([0,0])
goal = array([3,3])
s = Step(array([0,0]), 4, 0)
g = Step(array([3,3]), 4, 0)
obstacles = [array([1,0]), array([2,2]), array([0,1])]
obstacles2 = [array([1,0]), array([2,2]), array([0,1]), array([2,3]), array([3,4]), array([4,3]), array([4,2]), array([3,1])]
o = set(map(lambda x: Step(x, 3, 2), obstacles))
from timeit import timeit
