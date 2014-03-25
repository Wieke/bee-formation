import sys
sys.path.append("..")

from BaseBee import BaseBee
import numpy as np

class GravityBee(BaseBee):
    #Static methods
    def worldConstraints():
        return {"occlusion":False, "collision":False, "comrange":0}
    
    def name():
        return "Gravity bee"

    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        self.finished = False
        
    def behave(self, perception):
        if self.awake:
            if not self.finished:
                r = self.generator.random()
                bees, communication, feedback = perception
                comLocs = []
                comComs = []
                for i in range(0,len(communication)):
                    comLoc, comCom = communication[i]
                    comLocs.append(comLoc)
                    comComs.append(comCom)
                if len(comComs) == 0:
                    comComs = [None]
                    
                centerofmass = np.around(sum(bees)/len(bees))

                if centerofmass[0] > 0:
                    return (np.array([1,0]), None)
                elif centerofmass[0] < 0:
                    return (np.array([-1,0]), None)
                elif centerofmass[1] > 0:
                    return (np.array([0,1]), None)
                elif centerofmass[1] < 0:
                    return (np.array([0,-1]), None)
                else:
                    if all(comComs):
                        self.finished = True
                        return (None, True)
                    else:
                        return (np.array([0,0]), True)
            else:
                return (None, True)
            
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
            return (np.array([0,0]), None)
