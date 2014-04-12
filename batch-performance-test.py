from multiprocessing import Pool
from sys import path
path.append("source")
path.append("source//bees")
from numpy import array, arange, zeros
from World import World
from itertools import product as iterprod
from GordonBee import GordonBee as GB
from GordonBeeOccluded import GordonBeeOccluded as GBO
from GordonBeeCollision import GordonBeeCollision as GBC
import random
from time import time
from csv import writer

def formations():
    formations = []
    
    formations.append(list(iterprod(arange(0,3),arange(0,3))))
    
    formations.append(list(iterprod(arange(0,4),arange(0,4))))
    
    f = list(iterprod(arange(0,5),arange(0,5)))
    for x in [18, 17, 16, 13, 11, 8, 7, 6 ]:
        del f[x]
    formations.append(f)
    
    formations.append(list(iterprod(arange(0,8,2),arange(0,8,2))))
    
    f = list(iterprod(arange(0,3),arange(0,3)))
    f = f + list(iterprod(arange(8,11),arange(5,8)))
    formations.append(f)

    f = list(iterprod(arange(0,3),arange(0,3)))
    f = f + list(iterprod(arange(1,4),arange(1,4)))
    for x in [14, 13, 11, 10]:
        del f[x - 1]
    formations.append(f)

    i = 1001
    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,5),arange(0,5)))
        , 15))
    i += 1

    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,5),arange(0,5)))
        , 15))
    i +=1
    
    return formations

def printformation(formation):
    minx = formation[0][0]
    maxx = formation[0][0]
    miny = formation[0][1]
    maxy = formation[0][1]
    for x,y in formation:
        if minx > x:
            minx = x
        elif maxx < x:
            maxx = x
        if miny > y:
            miny = y
        elif maxy < y:
            maxy = y

    order = zeros((maxx - minx + 3, maxy - miny + 3))

    i = 1
    for x,y in map(lambda x: x - array([minx - 1,miny - 1]), formation):
        order[x,y] = i
        i+= 1

    out = str(str(order))
    out = out.replace(" 0.","   ")

    print(out)
    
def worlds(seed): ## Returns 24 tests per seed
    worlds = []
    f = formations()
    for fn in range(0,len(f)):
        #worlds.append((GB,f[fn].copy(),fn,seed))
        #worlds.append((GBO,f[fn].copy(),fn,seed))
        worlds.append((GBC,f[fn].copy(),fn,seed))
    return worlds

def do_work(a):
    beetype, formation, formnumber, seed = a
    w = World(beetype,
              len(formation),
              len(formation)*2,
              len(formation)*2,
              {"seed":0, "formation":formation},
              seed,
              True)

    i = 0
    while not w.finished and  i < 1000:
        w.stepForward()
        i += 1


    if not i < 1000:
        #print(seed, beetype.__name__, "formation", formnumber, "  DNF!")
        return [seed, beetype.__name__, formnumber, "DNF", "DNF", w.beeSteps, w.sizeOfWorld]        
    else:
        #print(seed, beetype.__name__,"formation",formnumber, "done!")
        return [seed, beetype.__name__, formnumber, w.totalStates, w.timeToFinish, w.beeSteps, w.sizeOfWorld]        
    
##if __name__=="__main__":
##    with open('results.csv', 'w') as csvfile:
##        file = writer(csvfile)
##        file.writerow(["seed","beetype","formation","totalStates","timeToFinish","beeSteps","sizeOfWorld"])
##
##    p = Pool(8)
##    
##    for seed in range(0,25):
##        res = p.map(do_work, worlds(seed))
##
##        with open('results.csv', 'a') as csvfile:
##            file = writer(csvfile)
##            for row in res:
##                file.writerow(row)



p = Pool(8)
res = p.map(do_work, worlds(0))
