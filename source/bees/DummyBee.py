import sys
sys.path.append("..")

from BaseBee import BaseBee
import numpy as np

class DummyBee(BaseBee):
    #Static methods 
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}

    def name():
        return "Dummy Bee"
    
    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)

    def behave(self, perception):
        if self.awake:
            return (np.array([0,0]), None)
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
            return (np.array([0,0]), None)

    
