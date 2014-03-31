import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around, dot, arange
from sys import maxsize
from itertools import product as iterprod
from World import lineofsight

class GordonBeeOccluded(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":True, "collision":False, "comrange":0}
    
    def name():
        return "Gordon bee occluded"

    def comkeys():
        return ["flag", "phase", "order", "free"]
    
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
        self.nr_of_bees = 0
        
    def behave(self, perception):
        self.time += 1
        self.perception = perception
        pos, com, success = self.perception
        if self.nr_of_bees < len(pos):
            self.nr_of_bees = len(pos)
        if self.awake:
            
            if self.phase == 1:
                """Move towards the center of mass"""

                if not (self.majority_is_here() or self.all_bees_are_here()):
                    self.destination = self.center_of_bees()
                else:
                    self.destination = None

                if self.all_bees_are_here():
                    self.flag = True

                if self.flag and self.all_bees_raised_flag():
                        self.phase = 2
                        self.position = array([0,0])
                        self.destination = None
                        
            elif self.phase == 2:
                """Move towards most popular [1,0]"""

                if self.destination is None:
                    self.destination = array([1,0])
                    self.flag = False
                    self.debugInformation = "Moving to 1,0"
                elif self.arrived() and (self.nr_of_bees_at(array([0,0])) == 0 or self.flag):
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


            elif self.phase == 5:
                if self.destination is None:
                    self.formation = self.normalize(self.formation)
                    self.destination = self.formation[self.order]
                else:
                    if self.arrived():
                        self.phase = 6

            elif self.phase == 6:
                return (None, {"flag":self.flag, "phase":self.phase, "order":self.order})
                
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1

        if self.order_formation is not None:                
            return (self.move().copy(), {"flag":self.flag, "phase":self.phase, "order":self.order, "free":len(self.order_formation)})
        else:
            return (self.move().copy(), {"flag":self.flag, "phase":self.phase, "order":self.order})

    def majority_is_here(self):
        pos, com, success = self.perception
        here = 0
        not_here = 0

        for x in pos:
            if array_equal(x,array([0,0])):
                here += 1
        
        return here > (self.nr_of_bees - here)

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
        
    def update_order_formation_availeble(self):
        pos, com, success = self.perception
        new = self.generate_order_formation(len(pos) + 1)
        free = lambda x: self.nr_of_bees_at(x) == 0
        taken = lambda x: self.nr_of_bees_at(x) == 1

        is_in = lambda x, y: any(map(lambda z: array_equal(x,z),y))

        guaranteed_free = [x for x in new if free(x) and self.can_i_see(x) and not is_in(x, self.order_formation)]

        self.order_formation = [x for x in self.order_formation if not (taken(x) and self.can_i_see(x))]

        for x in guaranteed_free:
            self.order_formation.append(x)

        if len(self.order_formation) == 0:
            self.order_formation = [x for x in new if not (taken(x) and self.can_i_see(x))]

        self.debugInformation = str(self.order_formation)

    def everyone_in_order_formation(self):
        one_at = lambda x: self.nr_of_bees_at(x) == 1 or array_equal(x,self.position)
        return all(map(one_at, self.order_formation))

    def everyone_confirmed_order(self):
        is_confirmed = lambda x: self.nr_of_bees_at(x + array([0,1])) == 1
        is_empty = lambda x: self.nr_of_bees_at(x) == 0 and self.nr_of_bees_at(x+array([0,1])) == 0
        is_origin = lambda x: array_equal(x,array([0,0])) or array_equal(x + array([0,1]),array([0,0]))
        condition = lambda z: is_confirmed(z) or is_empty(z) or is_origin(z) or array_equal(z,self.position)
        return all(map(condition, self.order_formation))

    def empty_position_in_order_formation(self):
        return min([ x for x in self.order_formation
          if self.nr_of_bees_at(x) == 0 and not array_equal(x, array([0,0]))], key=self.distance)

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
        limpos = list(filter(lambda x: not array_equal(x,array([0,0])),pos))        
        if len(limpos) > 0:
            return around(sum(limpos)/len(limpos))
        else:
            return around(sum(pos)/len(pos))

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
        if self.phase == 1:
            return array_equal(self.destination, array([0,0]))
        elif self.phase > 1:
            return array_equal(self.destination, self.position)
        else:
            print("This is not supposed to happen")
            return False

    def generate_order_formation(self, n):
        mindist = maxsize
        for i in range(1,n):
            if abs(int(n/i + 0.5) - (i*2 -1)) < mindist:
                mindist = abs(int(n/i + 0.5) - (i*2 -1))
            else:
                y = int(n/(i - 1) + 0.5)
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

    def distance(self, p):
        return pow(pow(p[0]-self.position[0],2) + pow(p[1]-self.position[1],2), 0.5)
    
    def move(self):
        """ Determines direction to move in order to reach destination, updates position. """
        """ Responsible for transformations """
        if self.destination is None or not self.awake:
            return array([0,0])

        if self.phase == 2:
            point = self.destination.copy() - self.position
        elif self.phase > 2:
            point = self.transform(self.destination.copy() - self.position)
        else:
            point = self.destination.copy()
        
        if point[0] > 0:
            move = array([1,0])
        elif point[0] < 0:
            move = array([-1,0])
        elif point[1] > 0:
            move = array([0,1])
        elif point[1] < 0:
            move = array([0,-1])
        else:
            move = array([0,0])

        if self.phase == 2:
            self.position += move
        elif self.phase > 2:
            self.position += self.transform2(move)


        return move
            
    def can_i_see(self, point):
        pos, com, success = self.perception
        if self.phase == 2:
            point = point.copy() - self.position
        elif self.phase > 2:
            point = self.transform(point.copy() - self.position)
        else:
            point = self.destination.copy()

        return lineofsight(point, array([0,0]), pos)
 
