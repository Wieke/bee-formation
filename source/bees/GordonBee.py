import sys
sys.path.append("..")

from BaseBee import BaseBee
from numpy import array, array_equal

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
        
    def behave(self, perception):
        if self.awake:
            r = self.generator.random()
            bees, communication = perception
            
            centerofmass = np.around(sum(bees)/len(bees))

            output = {"flag":False}
            move = array([0,0])

            if centerofmass[0] > 0:
                move = array([1,0]
            elif centerofmass[0] < 0:
                move = array([-1,0]
            elif centerofmass[1] > 0:
                move = array([0,1]
            elif centerofmass[1] < 0:
                move = array([0,-1]
            elif all(map(lambda x: array_equal(array([0,0]),x),bees)):
                output = {"flag":True}
                
            return (move, output)
            
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
            return (np.array([0,0]), None)
