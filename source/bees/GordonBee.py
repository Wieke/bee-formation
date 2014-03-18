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
        return ["flag"]
    
    #Non-static methods
    def __init__(self, args):
        BaseBee.__init__(self, args)
        self.flag = False
        self.position = None
        self.currentphase = self.phase1
        self.time = 0
        self.f = None
        self.fi = None
        self.trans = None
        self.everyoneatorigin = None
        self.global10 = None
        
    def behave(self, perception):
        move = array([0,0])
        if self.awake:
            
            move = self.currentphase(perception)


            if move is None:
                move = array([0,0])
            if self.position is not None:
                if self.trans is not None:
                    self.position += dot(move, self.trans)
                else:
                    self.position += move
        else:
            if self.sleepCounter <= 0:
                self.awake = True
                self.sleepCounter = 0
            else:
                self.sleepCounter -= 1
        
        self.time += 1
        return (move, {"flag":self.flag})

    def debug(self, text):
        self.debugInformation = str(self.time) + ": " + text

    def phase1(self, perception):
        bees, communication = perception
        
        centerofmass = around(sum(bees)/len(bees))

        self.debug("Finding Center of Mass")

        if not array_equal(centerofmass,array([0,0])):
            return self.moveto(centerofmass)
        elif self.flag:
            if len(communication) != 0:
                loc, flag = zip(*communication)
                
                if all(map(lambda x: x['flag'], flag)):
                    self.debug("Center of mass agreed upon, proceding to phase2.")
                    self.currentphase = self.phase2
                    self.everyoneatorigin = True
            else:
                self.debug("Center of mass agreed upon, proceding to phase2.")
                self.currentphase = self.phase2
                self.everyoneatorigin = True
        elif all(map(lambda x: array_equal(array([0,0]),x),bees)):
            self.flag = True
            self.position = array([0,0])
            self.f  = lambda x: x + self.position
            self.fi = lambda x: x - self.position
            
            self.debug("Found center of mass, internal position set to (0,0).")

    def moveto(self, point):
        if self.fi is not None:
            point = self.fi(point)
        
        if point[0] > 0:
            return array([1,0])
        elif point[0] < 0:
            return array([-1,0])
        elif point[1] > 0:
            return array([0,1])
        elif point[1] < 0:
            return array([0,-1])
        else:
            return array([0,0])

    def phase2(self, perception):
        bees, communication = perception

        bees = list(map(self.f, bees))
        
        if self.flag and self.everyoneatorigin:
            self.flag = False
            return array([1,0])
        elif self.everyoneatorigin:
            if all(map(lambda x: not array_equal(x,array([0,0])),bees)):
                self.everyoneatorigin = False
                self.debug("Nobody at origin anymore.")
        elif self.flag:
            if len(communication) != 0:
                loc, flag = zip(*communication)
                
                if all(map(lambda x: x['flag'], flag)):
                    self.debug("[1,0] agreed upon, proceding to phase3.")
                    self.currentphase = self.phase3
            else:
                self.debug("[1,0] agreed upon, proceding to phase3.")
                self.currentphase = self.phase3
        else:
            right = 0
            left = 0
            up = 0
            down = 0
            for pos in bees:
                if array_equal(pos,array([1,0])):
                    right += 1
                elif array_equal(pos,array([-1,0])):
                    left += 1
                elif array_equal(pos,array([0,1])):
                    up += 1
                elif array_equal(pos,array([0,-1])):
                    down += 1

            if right == max(right,left,up,down):
                self.debug("Right is favored")
                best = array([1,0])
            elif left == max(right,left,up,down):
                self.debug("Left is favored")
                best = array([-1,0])
            elif up == max(right,left,up,down):
                self.debug("Up is favored")
                best = array([0,1])
            else:
                self.debug("Down is favored")
                best = array([0,-1])

            if not array_equal(best, self.position):
                return self.moveto(best)
            else:
                if all(map(lambda x: array_equal(best,x), bees)):
                    self.debug("All have arrived at agreed [1,0], setting flag.")
                    self.global10 = best
                    self.flag = True
                else:
                    self.debug("Arrived at argreed best.")

    def phase3(self, perception):
        bees, communication = perception
        if not array_equal(self.position, array([0,0])):
            return self.moveto(array([0,0]))
        elif self.flag:
            if len(communication) != 0:
                loc, flag = zip(*communication)
                
                if all(map(lambda x: x['flag'], flag)):
                    self.debug("Everybody back at origin, go to phase4.")
                    self.everyoneatorigin = True
                    self.currentphase = self.phase4
            else:
                self.debug("Everybody back at origin, go to phase4.")
                self.everyoneatorigin = True
                self.currentphase = self.phase4
        else:
            self.debug("I am is at origin")
            if all(map(lambda x: array_equal(array([0,0]),x),bees)):
                self.flag = True


    def phase4(self, perception):
        bees, communication = perception

        bees = list(map(self.f, bees))

        if self.global10[1] == 0:
            rotate = False
        else:
            rotate = True
        
        if self.flag and self.everyoneatorigin:
            self.flag = False
            if rotate:
                return array([1,0])
            else:
                return array([0,1])
        elif self.everyoneatorigin:
            if all(map(lambda x: not array_equal(x,array([0,0])),bees)):
                self.everyoneatorigin = False
                self.debug("Nobody at origin anymore.")
        elif self.flag:
            if len(communication) != 0:
                loc, flag = zip(*communication)
                
                if all(map(lambda x: x['flag'], flag)):
                    self.debug("[1,0] agreed upon, proceding to phase3.")
                    self.currentphase = self.phase5
            else:
                self.debug("[1,0] agreed upon, proceding to phase3.")
                self.currentphase = self.phase5
        else:
            up = 0
            down = 0
            
            for pos in bees:
                if array_equal(pos,array([0,1])):
                    up += 1
                elif array_equal(pos,array([0,-1])):
                    down += 1

            if up == max(up,down):
                self.debug("Up is favored")
                if rotate:
                    best = array([1,0])
                else:
                    best = array([0,1])
            else:
                self.debug("Down is favored")
                if rotate:
                    best = array([-1,0])
                else:
                    best = array([0,-1])

            if not array_equal(best, self.position):
                return self.moveto(best)
            else:
                if all(map(lambda x: array_equal(best,x), bees)):
                    self.debug("All have arrived at agreed [1,0], setting flag.")
                    self.global01 = best
                    self.flag = True
                else:
                    self.debug("Arrived at argreed best.")

    def phase5(self, perception):
        self.debug("Arrived at phase5.\nglobal10=" + str(self.global10) + "\nglobal01="+str(self.global01))
        
