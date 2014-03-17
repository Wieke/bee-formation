import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal, around

class GordonBee(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}
    
    def name():
        return "Gordon bee"

    def comkeys():
        return ["flag"]
    
    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        self.flag = False
        
    def behave(self, perception):
        move = array([0,0])
        if self.awake:
            r = self.generator.random()
            bees, communication = perception
            
            centerofmass = around(sum(bees)/len(bees))

            move = array([0,0])
            self.debugInformation = "Finding center of blas."
            
            if centerofmass[0] > 0:
                move = array([1,0])
            elif centerofmass[0] < 0:
                move = array([-1,0])
            elif centerofmass[1] > 0:
                move = array([0,1])
            elif centerofmass[1] < 0:
                move = array([0,-1])
            elif all(map(lambda x: array_equal(array([0,0]),x),bees)):
                self.flag = True
                            
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1

        return (move, {"flag":self.flag})
