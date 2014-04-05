import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around, dot, arange
from sys import maxsize
from itertools import product as iterprod
from math import ceil
from pathfinding import findpathtoclosest

class GordonBeeCollision(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":True, "comrange":1}
    
    def name():
        return "Gordon bee collision"

    def comkeys():
        return ["flag", "phase", "confirmation", "order"]
    
    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        self.flag = False
        self.phase = 1
        self.destination = None
        self.trans = None
        self.position = None
        self.swapxy = False
        self.flipx = False
        self.flipy = False
        self.order = None
        self.order_formation = None
        self.time = 0
        self.cluster_radius = None
        self.lastmove = None
        self.closest_i_could_get = None
        
    def behave(self, perception):
        self.time += 1
        self.perception = perception
        pos, com, success = self.perception

        if self.lastmove is not None and self.position is not None and success:
            if self.phase == 2:
                self.position += self.lastmove
            elif self.phase > 2:
                self.position += self.transform2(self.lastmove)
        
        if self.awake:
            
            if self.phase == 1:
                """Move towards the center of mass"""

                self.destination = self.center_of_bees()
                    
                if self.arrived() and self.all_bees_in_cluster(self.destination):
                    self.flag = True
                
                if self.flag and self.all_bees_raised_flag():
                    self.phase = 6
                    self.destination = None
                    self.position = array([0,0])
                        
            elif self.phase == 2:
                """Move towards most popular [1,0]"""

                if self.destination is None:
                    self.destination = array([int(self.cluster_radius*3),0])
                    self.flag = False
                    self.debugInformation = "Moving to 1,0"
                    
                if self.arrived() and (self.nr_of_bees_at(array([0,0])) == 0 or self.flag):
                    self.debugInformation = "Arrived and 0,0 is empty"
                    direction = [array([0,1]), array([1,0]), array([0,-1]), array([-1,0])]
                    
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    self.destination = most_popular    

                    if self.arrived() and self.all_bees_are_here():
                        self.flag = True
                        self.debugInformation = "Arrived at most popular and everyone is here"

                    if self.flag and (self.all_bees_raised_flag() or self.nr_of_bees_at(self.position)==0):
                        self.phase = 3
                        self.destination = None 
                        self.debugInformation = "Everyone has raised flag"

                        most_popular = self.position
                        if array_equal(most_popular, array([0,1])):
                            self.swapxy = True
                        elif array_equal(most_popular, array([0,-1])):
                            self.swapxy = True
                            self.flipx = True
                        elif array_equal(most_popular, array([-1,0])):
                            self.flipx = True
                            
                        self.position = array([1,0])


            elif self.phase == 3:
                """Move towards most popular [0,1]"""
                
                if self.destination is None:
                    self.destination = array([0,1])
                    self.flag = False
                    self.debugInformation = "Moving to 0,1"
                    
                if self.arrived() and (self.nr_of_bees_at(array([0,0])) == 0 or self.flag):
                    self.debugInformation = "Arrived and 0,0 is empty"
                    direction = [array([0,1]), array([0,-1])]
                    
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    self.destination = most_popular    

                    if self.arrived() and self.all_bees_are_here():
                        self.flag = True
                        self.debugInformation = "Arrived at most popular and everyone is here"

                    if self.flag and (self.all_bees_raised_flag() or self.nr_of_bees_at(self.position)==0):
                        self.phase = 4
                        self.destination = None
                        self.debugInformation = "Everyone has raised flag"
                        
                        most_popular = self.position
                        if most_popular[1] == -1:
                            self.flipy = True
                        self.position = array([1,0])

            elif self.phase == 4:
                """ Move to ordering formation """

                self.debugInformation = "Phase 4"
                
                if self.order_formation == None:
                    self.order_formation = self.generate_order_formation(len(pos) + 1)
                    self.destination = self.empty_position_in_order_formation()

                if self.order is None and self.destination is not None:
                    if self.arrived():
                        if self.nr_of_bees_at(self.position) != 0 or self.nr_of_bees_at(self.position + array([0,1])) != 0:
                            self.destination = self.empty_position_in_order_formation()
                        elif self.nr_of_bees_at(self.position) == 0 and self.nr_of_bees_at(self.position + array([0,1])) == 0:
                            self.debugInformation = "Found My Spot"
                            self.destination = None
                elif self.destination is None and self.order is None and self.everyone_in_order_formation():
                    self.destination = self.position + array([0,1])
                    self.flag = False
                    for i in range(0,len(self.order_formation)):
                        if array_equal(self.order_formation[i], self.position):
                            self.order = i
                            break

                elif self.order is not None:
                    if self.everyone_confirmed_order():
                        self.destination = array([0,0])
                    
                    if self.arrived() and array_equal(self.position, array([0,0])):
                        if self.all_bees_are_here():
                            self.flag = True

                        if self.flag and (self.all_bees_raised_flag() or self.nr_of_bees_at(self.position)==0):
                            self.phase = 5
                            self.destination = None

            elif self.phase == 5:
                if self.destination is None:
                    self.formation = self.normalize(self.formation)
                    self.destination = self.formation[self.order]
                else:
                    if self.arrived():
                        self.phase = 6

            elif self.phase == 6:
                self.lastmove = None
                return (self.lastmove, {"flag":self.flag, "phase":self.phase, "order":self.order})
                
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1

        self.lastmove = self.move().copy()
        return (self.lastmove, {"flag":self.flag, "phase":self.phase, "order":self.order})

    def normalize(self, l):
        minx = l[0][0]
        miny = l[0][1]
        maxx = l[0][0]
        maxy = l[0][1]

        for x,y in l:
            if x > maxx:
                maxx = x
            if x < minx:
                minx = x
            if y > maxy:
                maxy = y
            if y < miny:
                miny = y

        mod = array([int(minx + (maxx - minx)/2),int(miny + (maxy - maxy)/2)])
        return [x - mod for x in l]

    def all_bees_in_cluster(self, cluster_position):
        pos, com, success = self.perception
        if self.cluster_radius is None:
            self.cluster_radius = GordonBeeCollision.calculate_cluster_radius(len(pos) + 1)

        within_radius = lambda x: self.distance(x, cluster_position) <= self.cluster_radius

        return all(map(within_radius, pos)) and within_radius(array([0,0]))        

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

    def center_of_bees(self):
        """ Return the center of mass of the bees """
        pos, com, success = self.perception
        return around(sum(pos)/(len(pos) + 1))

    def all_bees_are_here(self):
        """ Returns true if all bees are at the same point. """
        pos, com, success = self.perception
        return all(map(lambda x: array_equal(x,array([0,0])),pos))

    def all_bees_raised_flag(self):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        return all(map(lambda x: x[1]["flag"], com))

    def all_bees_at_phase(self, phase):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        return all(map(lambda x: x[1]["phase"] == phase, com))
    
    def all_bees_lowered_flag(self):
        """ Returns true if all bees have raised their flag"""
        pos, com, success = self.perception
        return all(map(lambda x: not x[1]["flag"], com))

    def arrived(self):
        """ Return true if self.destination equals has been reached """
        """ Responsible for transformations """

        if self.selected and not self.flag:
            import code
            code.interact(local=locals())

            
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
        else:
            print("This is not supposed to happen")
            return False

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
            y = ceil(leftover / 8) - 1
        
        distance = pow(pow(x, 2) + pow(y,2), 0.5)
        return distance
    
    def move(self):
        """ Determines direction to move in order to reach destination, updates position. """
        """ Responsible for transformations """
        pos, com, success = self.perception
        if self.destination is None or not self.awake:
            return array([0,0])

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
        else:
            move = array([0,0])

        return move
