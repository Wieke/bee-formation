import sys
sys.path.append("..")
from BaseBee import BaseBee

class DummyBee(BaseBee):

    def __init__(self):
        self.awake = True
    
    def arguments():
        return None

    def move(self, perception):
        return (0,0)

    def shortRangeCommunicate(self, perception):
        return None
    
    def name():
        return "Dummy Bee"
    
