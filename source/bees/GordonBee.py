import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around, dot, arange
from sys import maxsize
from itertools import product as iterprod

class GordonBee(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}
    
    def name():
        return "Gordon bee"

    def comkeys():
        return ["flag", "phase"]
    
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
    
    def behave(self, perception):
        
        self.perception = perception
        if self.awake:
            
            if self.phase == 1:
                """Move towards the center of mass"""

                self.destination = self.center_of_bees()
                    
                if self.arrived() and self.all_bees_are_here():
                    self.flag = True
                
                if self.flag and self.all_bees_raised_flag():
                        self.phase = 2
                        self.destination = None
                        self.position = array([0,0])
                        
            elif self.phase == 2:
                """Move towards most popular [1,0]"""

                if self.destination is None:
                    self.destination = array([1,0])
                    self.flag = False
                    self.debugInformation = "Moving to 1,0"
                    
                if self.arrived() and self.nr_of_bees_at(array([0,0])) == 0:
                    self.debugInformation = "Arrived and 0,0 is empty"
                    direction = [array([0,1]), array([1,0]), array([0,-1]), array([-1,0])]
                    
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    self.destination = most_popular    

                    if self.arrived() and self.all_bees_are_here():
                        self.flag = True
                        self.debugInformation = "Arrived at most popular and everyone is here"
                        if array_equal(most_popular, array([0,1])):
                            self.swapxy = True
                        elif array_equal(most_popular, array([0,-1])):
                            self.swapxy = True
                            self.flipx = True
                        elif array_equal(most_popular, array([-1,0])):
                            self.flipx = True
                            
                        self.position = array([1,0])

                    if self.flag and self.all_bees_raised_flag():
                        self.phase = 3
                        self.destination = None 
                        self.debugInformation = "Everyone has raised flag"

            elif self.phase == 3:
                """Move towards most popular [0,1]"""
                
                if self.destination is None:
                    self.destination = array([0,1])
                    self.flag = False
                    self.debugInformation = "Moving to 0,1"
                    
                if self.arrived() and self.nr_of_bees_at(array([0,0])) == 0:
                    self.debugInformation = "Arrived and 0,0 is empty"
                    direction = [array([0,1]), array([0,-1])]
                    
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    self.destination = most_popular    

                    if self.arrived() and self.all_bees_are_here():
                        self.flag = True
                        self.debugInformation = "Arrived at most popular and everyone is here"
                        self.position = array([1,0])
                        if most_popular[1] == -1:
                            self.flipy = True

                    if self.flag and self.all_bees_raised_flag():
                        self.phase = 4
                        self.destination = None
                        self.debugInformation = "Everyone has raised flag"

            elif self.phase == 4:
                """ Move to ordering formation """   
                
                self.destination = array([1,3])          
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
                
        return (self.move().copy(), {"flag":self.flag, "phase":self.phase})

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

    def order_formation(self, n):
        mindist = maxsize
        for i in range(1,n):
            if abs(int(n/i + 0.5) - (i*2 -1)) < mindist:
                mindist = abs(int(n/i + 0.5) - (i*2 -1))
            else:
                y = int(n/(i - 1) + 0.5)
                x = i - 1
                print("y ", y," x ",x)
                break

        return list(iterprod(arange(-1*int(y/2),int(y/2)+1),
                             arange(-1*int((x*2-1)/2), int((x*2-1)/2)+1, 2)))

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

        self.debugInformation  = "Destination = " + str(self.destination) + "\nPosition = " + str(self.position)
        self.debugInformation += "\nSwapxy = " + str(self.swapxy) + "\nFlipx = " + str(self.flipx) + "\nFlipy = " + str(self.flipy)
        self.debugInformation += "\nPoint = " + str(point) + "\nMove = " + str(move) + "\nTransform(Move)= " + str(self.transform(move))
        self.debugInformation += "\nTransformation = " + str(self.transformation)

        if self.phase == 2:
            self.position += move
        elif self.phase > 2:
            self.position += self.transform2(move)


        return move
            

 
