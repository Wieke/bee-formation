import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around, dot

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
                    
                if self.arrived() and self.nr_of_bees_at(array([0,0])) == 0:
                    direction = [array([0,1]), array([1,0]), array([0,-1]), array([-1,0])]
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    if array_equal(most_popular, self.position) and self.all_bees_are_here():
                        self.flag = True

                    if self.flag and self.all_bees_raised_flag():
                        self.phase = 3
                        self.destination = None
                        self.trans = most_popular

                    self.destination = most_popular                   
                    
                
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
                
        return (self.move(), {"flag":self.flag, "phase":self.phase})

    def nr_of_bees_at(self, point):
        """ Returns the number of bees at point """
        """ Responsible for transformations """
        pos, com = self.perception

        if self.phase == 2:
            point += point - self.position

        return sum(map(lambda x: array_equal(point,x),pos))

    def center_of_bees(self):
        """ Return the center of mass of the bees """
        pos, com = self.perception
        return around(sum(pos)/len(pos))

    def all_bees_are_here(self):
        """ Returns true if all bees are at the same point. """
        pos, com = self.perception
        return all(map(lambda x: array_equal(x,array([0,0])),pos))

    def all_bees_raised_flag(self):
        """ Returns true if all bees have raised their flag"""
        pos, com = self.perception
        return all(map(lambda x: x[1]["flag"], com))


    def arrived(self):
        """ Return true if self.destination equals has been reached """
        """ Responsible for transformations """
        if self.phase == 1:
            return array_equal(self.destination, array([0,0]))
        elif self.phase == 2:
            return array_equal(self.destination, self.position)
        else:
            print("This is not supposed to happen")
            return False

    def move(self):
        """ Determines direction to move in order to reach destination, updates position. """
        """ Responsible for transformations """
        if self.destination is None or not self.awake:
            return array([0,0])

        if self.phase == 2:
            point = self.destination - self.position
        else:
            point = self.destination
        
        if point[0] > 0:
            move = array([1,0])
        elif point[0] < 0:
            move = array([-1,0])
        elif point[1] > 0:
            move = array([0,1])
        elif point[1] < 0:
            move = array([0,-1])
        else:
            return array([0,0])

        if self.phase == 2:
            self.position += move

        return move
            

 
