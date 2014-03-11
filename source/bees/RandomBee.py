import sys
sys.path.append("..")

from random import Random
from BaseBee import BaseBee

class RandomBee(BaseBee):

    def __init__(self, args):
        self.awake = True
        self.generator = Random(args["seed"])

    def arguments():
        return {"seed" : int}

    def move(self, perception):
        r = self.generator.random()
        if r < 0.25:
            return (0,1)
        elif r < 0.50:
            return (1,0)
        elif r < 0.75:
            return (0, -1)
        else:
            return (-1,0)

    def shortRangeCommunicate(self, perception):
        return None
    
    def name():
        return "Random bee"
