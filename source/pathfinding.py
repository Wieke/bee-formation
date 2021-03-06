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
    
def dumbfindpathtoclosest(start, goal, obstacles):
    bounds = getbounds(obstacles, goal)
    start = Step(start, distance(start, goal), 0)
    goal = Step(goal, None, None)
    steps = [start]
    i = 0
    while i < len(steps) and goal not in steps: 
        for x in possiblesteps(steps[i],goal,obstacles, bounds):
            if x not in steps:
                steps.append(x)
        i += 1
        
    if goal in steps:
        return (True, extractpath(goal, steps))
    else:
        minutil = min(steps).util
        closest_to_target = [x for x in steps if x.util == minutil]
        closest_to_me = min(closest_to_target,
                            key=lambda x: distance(start.pos,x.pos))
        return (False, extractpath(closest_to_me,steps))

    
def findpathtoclosest(start, goal, obstacles):
    if array_equal(start,goal):
        return (True, [])
    bounds = getbounds(obstacles, goal, start)
    start = Step(start, distance(start, goal), 0)
    goal = Step(goal, None, None)
    steps = [start]
    openable = [start]
    i = 0
    
    while len(openable) > 0 and goal not in steps and i < 15:
        i += 1
        o = min(openable)
        openable.remove(o)
        for x in possiblesteps(o, goal, obstacles, bounds):
            if x not in steps:
                steps.append(x)
                openable.append(x)
                
    if goal in steps:
        return (True, extractpath(goal, steps))
    else:
        minutil = min(steps).util
        closest_to_target = [x for x in steps if x.util == minutil]
        closest_to_me = min(closest_to_target,
                            key=lambda x: distance(start.pos,x.pos))
        return (False, extractpath(closest_to_me,steps))

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
        current = min(filter(condition, steps), key=lambda x: distance(goal.pos,x.pos))
        path.append(current)

    path.reverse()
    return [ x.pos for x in path[1:]]
        

def getbounds(obstacles, goal, start):
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

    x,y = start
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
