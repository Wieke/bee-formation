import sys
sys.path.append("..")

from BaseBee import BaseBee
import numpy as np

class RandomBee(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}
    
    def name():
        return "Random bee"

R    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        

    def behave(self, perception):
        r = self.generator.random()
        if r < 0.25:
            return (np.array([0,1]), None)
        elif r < 0.50:
            return (np.array([1,0]), None)
        elif r < 0.75:
            return (np.array([0,-1]), None)
        else:
            return (np.array([-1,0]), None)
