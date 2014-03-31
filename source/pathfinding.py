from numpy import array, array_equal

class Path(object):
    def __init__(self, parent, position, obstacles, heuristic):
        self.parent = parent
        self.heuristic = heuristic
        self.obstacles = obstacles
        self.position = position
        self.children = list()
        self.potentials = list(filter(self.is_free,
                        [self.position + array([1,0]),
                        self.position + array([0,1]),
                        self.position + array([-1,0]),
                        self.position + array([0,-1])]))
        if len(self.potentials)==0:
            self.fully_open = True
        else:
            self.fully_open = False
        self.fitness = heuristic(position)

    def open(self):
        if not self.fully_open:
            c = min(self.potentials, key=self.heuristic)
            
            for i in range(0,len(self.potentials)):
                if array_equal(self.potentials[i],c):
                    self.potentials.pop(i)
                    break

            self.children.append(Path(self, c, self.obstacles, self.heuristic))

            if len(self.potentials) == 0:
                self.fully_open = True         

    def is_free(self, point):
        if self.parent is not None:
            if array_equal(point, self.parent.position):
                return False
        else:
            return not any(map(lambda y: array_equal(point,y),self.obstacles))

    def __str__(self):
        return str(self.fitness) + " (" + str(self.position[0]) + "," + str(self.position[1]) + ")"

    def __repr__(self):
        r = "<" + str(self)
        if len(self.children) > 0:
            r += " "
            for c in self.children:
                r += repr(c)

        r += ">"

        return r

def aStar(begin, end, obstacles):
    print("MUEH")

def distance(p, q):
        return pow(pow(p[0]- q[0],2) + pow(p[1]- q[1],2), 0.5)


p = array([0,0])
obstacles = [array([1,0]), array([2,2]), array([0,1])]
t = Path(None, p, obstacles, lambda x: distance(x, array([4,4])))
