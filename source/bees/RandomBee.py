import sys
sys.path.append("..")

from BaseBee import BaseBee
import numpy as np

class RandomBee(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}
    
    def name():
        return "Random bee2"

    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        
    def behave(self, perception):
        if self.awake:
            r = self.generator.random()
            if r < 0.25:
                return (np.array([0,1]), None)
            elif r < 0.50:
                return (np.array([1,0]), None)
            elif r < 0.75:
                return (np.array([0,-1]), None)
            else:
                return (np.array([-1,0]), None)
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
            return (np.array([0,0]), None)
