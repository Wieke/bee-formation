import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around, dot, arange
from sys import maxsize
from itertools import product as iterprod
from math import ceil
from pathfinding import findpathtoclosest
from formation import buildorder

class GordonBeeCollision(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":True, "comrange":1}
    
    def name():
        return "Gordon bee collision"

    def comkeys():
        return ["flag", "consensus", "phase","order"]
    
    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        self.flag = False
        self.phase = 1
        self.destination = None
        self.position = None
        self.swapxy = False
        self.flipx = False
        self.flipy = False
        self.order = None
        self.time = 0
        self.cluster_radius = None
        self.lastmove = None
        self.closest_i_could_get = None
        self.nr_of_possible_neighbors = 8
        self.proper_formation = None
        self.nr_neighbors_flag_raised = 0
        self.internal_flag = False
        self.consensus = False
        self.center_of_cluster = None
        
    def behave(self, perception):
        self.time += 1
        self.perception = perception
        pos, com, success = self.perception

        if self.cluster_radius is None:
            self.cluster_radius = calculate_cluster_radius(len(pos) + 1)

        if self.lastmove is not None and self.position is not None and success:
            if self.phase == 2:
                self.position += self.lastmove
            elif self.phase > 2:
                self.position += self.transform2(self.lastmove)
            self.lastmove = None
        
        if self.awake:
            if self.phase == 1:
                """Move towards the center of mass"""

                if self.internal_flag:
                    self.update_flags()                

                if not self.internal_flag:
                    if self.arrived() and self.all_bees_in_cluster(self.destination) and self.position is None:
                        self.update_flags(self.destination)
                        self.position = array([0,0]) - self.destination
                    else:
                        self.set_destination(self.center_of_bees())
                else:
                    self.set_destination(None)
                
                if self.consensus_reached() and self.internal_flag and len(com) < 8:
                    self.phase = 2
                    self.set_destination(None)
                    self.internal_flag = False
                                            
            elif self.phase == 2:
                """Move towards most popular [1,0]"""
                d = int(self.cluster_radius*3) + 1
                direction = [array([0,d]), array([d,0]), array([0,-d]), array([-d,0])]
                if self.destination is None and not self.internal_flag:
                    self.set_destination(array([d,0]))
                    self.debugInformation = "Moving to 3*cluster_radius,0"
                    self.lower_flags()

                if self.internal_flag:
                    self.update_flags()

                if self.arrived() and (self.count_cluster_size_at(array([0,0])) == 0 or self.internal_flag):
                    self.debugInformation = "Arrived and 0,0 is empty"                    
                    most_popular = max(direction, key = self.count_cluster_size_at)

                    if not self.internal_flag:
                        self.set_destination(most_popular)
                    else:
                        self.set_destination(None)

                    if self.arrived() and self.all_bees_in_cluster(self.destination) and not self.internal_flag:
                        self.update_flags(self.destination)
                        self.debugInformation = "Arrived at most popular and everyone is here"

                if self.consensus_reached() and self.internal_flag and len(com) < 8:
                    self.phase = 3
                    self.set_destination(None)
                    self.debugInformation = "Everyone has raised flag"
                    self.internal_flag = False

                    most_popular = min(direction, key=self.distance)
                    
                    if array_equal(most_popular, array([0,d])):
                        self.swapxy = True
                        self.position = array([self.position[1],self.position[0]])
                    elif array_equal(most_popular, array([0,-d])):
                        self.swapxy = True
                        self.flipx = True
                        self.position = array([-self.position[1],self.position[0]])
                    elif array_equal(most_popular, array([-d,0])):
                        self.flipx = True
                        self.position = array([-self.position[0],self.position[1]])


            elif self.phase == 3:
                """Move towards most popular [0,1]"""
                d = int(self.cluster_radius*3) + 1
                direction = [array([0,d]), array([0,-d])]
                if self.destination is None and not self.internal_flag:
                    self.set_destination(array([0,d]))
                    self.debugInformation = "Moving to 0,1"
                    self.lower_flags()

                if self.internal_flag:
                    self.update_flags()
                    
                if self.arrived() and (self.count_cluster_size_at(array([0,0])) == 0 or self.internal_flag):
                    self.debugInformation = "Arrived and 0,0 is empty"
                    
                    most_popular = max(direction, key = self.count_cluster_size_at)

                    if not self.internal_flag:
                        self.set_destination(most_popular)
                    else:
                        self.set_destination(None)

                    if self.arrived() and self.all_bees_in_cluster(self.destination) and not self.internal_flag:
                        self.update_flags(self.destination)
                        self.debugInformation = "Arrived at most popular and everyone is here"
                        
                        if most_popular[1] < 0:
                            self.flipy = True
                            self.position = array([self.position[0],-self.position[1]])

                        self.order = self.determine_order()

                        if most_popular[1] < 0:
                            self.flipy = False
                            self.position = array([self.position[0],-self.position[1]])


                if self.consensus_reached() and self.internal_flag and len(com) < 8:
                    self.phase = 4
                    self.set_destination(None)
                    self.debugInformation = "Everyone has raised flag"
                    self.internal_flag = False
                    
                    most_popular = min(direction, key=self.distance)
                    if most_popular[1] < 0:
                        self.flipy = True
                        self.position = array([self.position[0],-self.position[1]])

            elif self.phase == 4:
                """ Move to formation """
                d = int(self.cluster_radius*3) + 1

                self.debugInformation = "Phase 4"

                if self.proper_formation is None:
                    """ Setting up formation build order """
                    self.proper_formation = [ (x[0], x[1] + array([0,-d])) for x in normalize(buildorder(self.formation))]
                    

                if self.destination is None and self.lower_orders_in_formation():
                    self.set_destination(self.proper_formation[self.order][1])
                else:
                    if array_equal(self.destination,self.position):
                        self.phase = 5
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
            
            self.lastmove = None
            if self.phase == 5:
                return (None, {"flag":self.flag,"consensus":self.consensus,"phase":self.phase,"order":self.order})
            else:
                return (array([0,0]), {"flag":self.flag,"consensus":self.consensus,"phase":self.phase,"order":self.order})

        if self.phase == 5:
            self.lastmove = None
            return (None, {"flag":self.flag,"consensus":self.consensus,"phase":self.phase,"order":self.order})

        m = self.move().copy()
        self.lastmove = m.copy()
        return (m, {"flag":self.flag,"consensus":self.consensus,"phase":self.phase,"order":self.order})

    def lower_orders_in_formation(self):
        if self.order == 0:
            return True

        rank = self.proper_formation[self.order][0]
        
        required = filter(lambda x: x[0] < rank, self.proper_formation)

        return all(map(lambda x: self.bee_at(x[1]), required))
        
    def lower_flags(self):        
        self.flag = False
        self.internal_flag = False
        self.consensus = False

    def count_cluster_size_at(self, cluster_position):
        pos = self.perception[0].copy()
        pos.append(array([0,0]))
        
        if self.phase == 2:
            point = cluster_position.copy() - self.position
        elif self.phase > 2:
            point = self.transform(cluster_position.copy() - self.position)
        else:
            point = cluster_position.copy()

        x, y = 0,0

        pos = [x - point for x in pos]
        
        count = 0
        
        while len(pos) > 0:

            if x == y and y == 0:
                positions_to_check = [(x,x)]
            elif x == y:
                positions_to_check = [(x,x),(x,-x),(-x,x),(-x,-x)]
            elif y == 0:
                positions_to_check = [(x,0),(-x,0),(0,x),(0,-x)]
            else:
                positions_to_check = [(x,y),(x,-y),(-x,y),(-x,-y),(y,x),(y,-x),(-y,x),(-y,-x)]


            indices = list(map(lambda a: find_by_array(pos, a), positions_to_check))
            count += sum(map(lambda a: a is not None, indices))
            if all(map(lambda a: a is not None, indices)):
                for i in reversed(sorted(indices)):
                    del pos[i]
            else:
                return count           

            if x == y:
                x += 1
                y = 0              
            else:
                y += 1

        return count



    def all_bees_in_cluster(self, cluster_position):
        pos, com, success = self.perception
        return self.count_cluster_size_at(cluster_position) == (len(pos)+1)   
    
    def everyone_in_order_formation(self):
        one_at = lambda x: self.nr_of_bees_at(x) == 1 or self.nr_of_bees_at(x+array([0,1])) == 1 or array_equal(x,self.position)
        return all(map(one_at, self.order_formation))

    def everyone_confirmed_order(self):
        is_confirmed = lambda x: self.nr_of_bees_at(x + array([0,1])) == 1
        is_empty = lambda x: self.nr_of_bees_at(x) == 0 and self.nr_of_bees_at(x+array([0,1])) == 0
        is_origin = lambda x: array_equal(x,array([0,0])) or array_equal(x + array([0,1]),array([0,0]))
        condition = lambda z: is_confirmed(z) or is_empty(z) or is_origin(z) or array_equal(z,self.position)
        return all(map(condition, self.order_formation))

    def empty_position_in_order_formation(self):
        return min([ x for x in self.order_formation
          if (self.nr_of_bees_at(x) == 0 and self.nr_of_bees_at(x + array([0,1])) == 0)],
                   key=self.distance)

    def nr_of_bees_at(self, point):
        """ Returns the number of bees at point """
        """ Responsible for transformations """
        pos, com, success = self.perception
        
        point = point.copy()
        
        if self.phase == 2:
            point -= self.position
        elif self.phase > 2:
            point = self.transform(point - self.position)

        return sum(map(lambda x: array_equal(point,x),pos))

    def bee_at(self, point):
        """ Returns the number of bees at point """
        """ Responsible for transformations """
        pos, com, success = self.perception
        
        point = point.copy()
        
        if self.phase == 2:
            point -= self.position
        elif self.phase > 2:
            point = self.transform(point - self.position)

        return any(map(lambda x: array_equal(point,x),pos))

    def center_of_bees(self):
        """ Return the center of mass of the bees """
        pos, com, success = self.perception
        return around(sum(pos)/(len(pos) + 1))

    def update_flags(self, new_center = None):
        pos, com, success = self.perception

        if not self.internal_flag:
            self.internal_flag = True

        if new_center is not None:
            self.center_of_cluster = new_center.copy()

        if self.position is not None:
            relative = self.position - self.center_of_cluster
        else:
            relative = array([0,0]) - self.center_of_cluster

        if array_equal(relative, array([0,0])):
            if all(map(lambda x: x[1]["flag"],com)):
                self.flag = True
                self.consensus = True
        elif relative[0] == relative[1]:
            modx = 1 if relative[0] > 0 else -1
            mody = 1 if relative[1] > 0 else -1
            filter_function = lambda c: any(map(lambda x: array_equal(x,c[0]),map(array,[(modx,0),(modx,mody),(0,mody)])))
            if all(map(lambda x: x[1]["flag"], filter(filter_function,com))):
                self.flag = True
        elif relative[0] > relative[1]:
            modx = 1 if relative[0] > 0 else -1
            f = list(filter(lambda x: array_equal(x,array([modx,0])), com))
            if len(f) > 0:
                if f[0][1]["flag"]:
                    self.flag = True
            else:
                self.flag = True
        else:
            mody = 1 if relative[1] > 0 else -1
            f = list(filter(lambda x: array_equal(x,array([0,mody])), com))
            if len(f) > 0:
                if f[0][1]["flag"]:
                    self.flag = True
            else:
                self.flag = True
                
        if any(map(lambda c: c[1]["consensus"],com)):
            self.consensus = True

    def consensus_reached(self):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        if len(com) > 0 and self.time > 1:
            return all(map(lambda x: x[1]["consensus"], com)) and self.consensus
        else:
            return True
        
    def all_bees_raised_flag(self):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        if len(pos) > 0:
            return all(map(lambda x: x[1]["flag"] == (self.nr_of_possible_neighbors + 1), com))
        else:
            return True

    def any_bee_raised_flag(self):
        pos, com, success = self.perception
        return any(map(lambda x: x[1]["flag"] == (self.nr_of_possible_neighbors + 1) if x[1] is not None else False, com))

    def any_bee_raised_something(self):
        pos, com, success = self.perception
        return any(map(lambda x: x[1]["flag"] > 0 if x[1] is not None else False, com))
    
    def all_bees_lowered_flag(self):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        return all(map(lambda x: x[1]["flag"] == 0, com))

    def arrived(self):
        """ Return true if self.destination equals has been reached """
        """ Responsible for transformations """
            
        if self.phase == 1:
            if self.closest_i_could_get is not None:
                return array_equal(self.closest_i_could_get, array([0,0]))
            else:            
                return array_equal(self.destination, array([0,0]))
        elif self.phase > 1:
            if self.closest_i_could_get is not None:
                return array_equal(self.closest_i_could_get, self.position)
            else:            
                return array_equal(self.destination, self.position)


    def generate_order_formation(self, n):
        mindist = maxsize
        for i in range(1,n):
            if abs(int(n/i + 1) - (i*2 -1)) < mindist:
                mindist = abs(int(n/i + 0.5) - (i*2 -1))
            else:
                y = int(n/(i - 1) + 1)
                x = i - 1
                break

        l = list(array(x) for x in iterprod(arange(-1*int(y/2),int(y/2)+1),
                                               arange(-1*int((x*2-1)/2), int((x*2-1)/2)+1, 2)))

        return l[0:n]

    def set_destination(self, dest):
        if not array_equal(self.destination,dest):
            self.closest_i_could_get = None
        self.destination = dest

    def transform2(self, p):
        point = p.copy()
        if self.swapxy:
            point = point[::-1]
        if self.flipx:
            point[0] = point[0]*-1
        if self.flipy:
            point[1] = point[1]*-1
        return point

    def transform(self, p):
        point = p.copy()
        if self.flipx:
            point[0] = point[0]*-1
        if self.flipy:
            point[1] = point[1]*-1
        if self.swapxy:
            point = point[::-1]
        return point

    def distance(self, p, q=None):
        if q is None:
            q = self.position
        return pow(pow(p[0]-q[0],2) + pow(p[1]-q[1],2), 0.5)

    def determine_order(self):
        pos, com, success = self.perception
        pos.append(array([0,0]))

        pos = list(map(self.transform2, pos))

        leaveorder = list(reversed(buildorder(pos)))

        for i in range(0,len(leaveorder)):
            if array_equal(array([0,0]),leaveorder[i][1]):
                return i
            i += 1

        print("HOLYSHITWTFBBQ! (This should not happen)")

    def randomStep(self):
        possible_steps = list(map(array,
                                  [(1,0),
                                   (0,1),
                                   (-1,0)
                                   (0,-1)]))

        pos, com, success = self.perception
        pos = pos.copy()
        for i in self.proper_formation:
            pos.append(self.transform(i[1] - self.position))

        no_go = lambda x: any(map(lambda y: array_equal(x,y),pos))

        for i in range(0,len(possible_steps)):
            if not no_go(i):
                return i

        return array([0,0])
            
        
    def move(self):
        """ Determines direction to move in order to reach destination, updates position. """
        """ Responsible for transformations """
        pos, com, success = self.perception        
        if self.destination is None:
            return array([0,0])

        if not self.awake:
            return array([0,0])


        if self.phase == 4 and self.proper_formation is not None:
            no_go = []
            for i in range(0,len(self.proper_formation)):
                if i != self.order and self.proper_formation[i][0] == self.proper_formation[self.order][0]:
                    no_go.append(self.transform(self.proper_formation[i][1] - self.position))
            pos = merge_array_lists(pos, no_go)

        if self.phase == 2:
            point = self.destination.copy() - self.position
        elif self.phase > 2:
            point = self.transform(self.destination.copy() - self.position)
        else:
            point = self.destination.copy()

        if not array_equal(point, array([0,0])):
            reachable, path = findpathtoclosest(array([0,0]), point, pos)
            if len(path) == 0:
                move = array([0,0])                    
            else:
                move = path[0]
            if not reachable and not array_equal(move,array([0,0])):
                if self.phase == 2:
                    self.closest_i_could_get = path[-1] + self.position
                elif self.phase > 2:
                    self.closest_i_could_get = self.transform2(path[-1]) + self.position
                else:
                    self.closest_i_could_get = path[-1]
            elif not reachable:
                if self.phase > 1:
                    self.closest_i_could_get = self.position
                else:
                    self.closest_i_could_get = array([0,0])
            else:
                self.closest_i_could_get = None

            if reachable and self.phase == 4 and array_equal(move,array([0,0])):
                move = self.randomStep()
                self.closest_i_could_get = None

        else:
            move = array([0,0])
            self.closest_i_could_get = None

        
        
        if self.selected:
            import code
            code.interact(local=locals())

        return move       

### Static Functions ###

def normalize(l):
    minx = l[0][1][0]
    miny = l[0][1][1]
    maxx = l[0][1][0]
    maxy = l[0][1][1]

    for z in l:
        x,y = z[1]
        if x > maxx:
            maxx = x
        if x < minx:
            minx = x
        if y > maxy:
            maxy = y
        if y < miny:
            miny = y

    mod = array([int(minx + (maxx - minx)/2),int(miny + (maxy - maxy)/2)])
    return [(x[0], x[1] - mod) for x in l]
    
def find_by_array(l, a):
    for i in range(0,len(l)):
        if l[i][0] == a[0] and l[i][1] == a[1]:
            return i
    return None

def calculate_cluster_radius(n):
    width = int(pow(n,0.5))

    if width % 2 == 0:
        width -= 1
    
    leftover = n - pow(width, 2)
    x = (width -1) / 2

    if leftover == 0:
        y = x
    elif leftover <= 4:
        x += 1
        y = 0
    elif ((4*(width + 2) - 4) - leftover) < 4:
        x += 1
        y = x
    else:
        x += 1
        y = ceil((leftover - 4) / 8)
    
    distance = pow(pow(x, 2) + pow(y,2), 0.5)
    return distance

def merge_array_lists(A,B):
    out = A.copy()
    is_in = lambda x: any(map(lambda y: array_equal(y,x),out))
    for x in B:
        if not is_in(x):
            out.append(x)
    return out
