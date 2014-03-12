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
        return (np.array([0,0]), None)
    

    
