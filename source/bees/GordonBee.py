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
        return ["flag", "phase", "pos"]
    
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
                    self.debugInformation = "Moving to 1,0"
                    
                if self.arrived() and self.nr_of_bees_at(array([0,0])) == 0:
                    self.debugInformation = "Arrived and 0,0 is empty"
                    direction = [array([0,1]), array([1,0]), array([0,-1]), array([-1,0])]
                    
                    most_popular = max(direction, key = self.nr_of_bees_at)

                    self.destination = most_popular    

                    if self.arrived() and self.all_bees_are_here():
                        self.flag = True
                        self.debugInformation = "Arrived at most popular and everyone is here"

                    if self.flag and self.all_bees_raised_flag():
                        self.phase = 3
                        self.destination = None
                        
                        if most_popular[0] != 0:
                            self.trans = array([most_popular,[0,1]])
                        else:
                            self.trans = array([most_popular,[1,0]])
                            
                        self.position = array([1,0])
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

                    if self.flag and self.all_bees_raised_flag():
                        self.phase = 4
                        self.destination = None

                        print(self.trans)
                        print(most_popular)
                        if self.trans[0][0] != 0:
                            self.trans = array([self.trans[0], most_popular])
                        else:
                            self.trans = array([self.trans[0], list(reversed(most_popular))])
                        print(self.trans)
                            
                        self.position = array([1,0])
                        self.debugInformation = "Everyone has raised flag"

            elif self.phase == 4:
                self.destination = array([1,3])
                
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
                
        return (self.move(), {"flag":self.flag, "phase":self.phase, "pos":str(self.position)})

    def nr_of_bees_at(self, point):
        """ Returns the number of bees at point """
        """ Responsible for transformations """
        pos, com = self.perception
        
        point = point.copy()
        
        if self.phase == 2:
            point -= self.position
        elif self.phase == 3:
            point = dot(self.trans, point - self.position)

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
        elif self.phase > 1:
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
            point = self.destination.copy() - self.position
        elif self.phase > 2:
            point = dot(self.trans, self.destination.copy() - self.position)
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

        self.debugInformation  = "destination=" + str(self.destination) +"\npoint=" + str(point)
        self.debugInformation += "\nposition=" + str(self.position) + "\nmove=" + str(move)

        if self.phase == 2:
            self.position += move
        elif self.phase > 2:
            self.position += dot(move, self.trans)

        self.debugInformation += "\nposition=" + str(self.position) + "\ntrans=" + str(self.trans)
        self.debugInformation += "\ntransformation=" + str(self.transformation)
        self.debugInformation += "\nOwnCoord=" + str(self.ownCoordinates)

        return move
            

 
