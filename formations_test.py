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

    i = 101
    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,5),arange(0,5)))
        , 10))
    i += 1

    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,10),arange(0,10)))
        , 10))
    i +=1
    
    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,10),arange(0,10)))
        , 15))
    i += 1

    random.seed(i)
    formations.append(random.sample(
        list(iterprod(arange(0,15),arange(0,15)))
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

    s = ""

    for line in order:
        for character in line:
            if character == 0:
                s += " "
            else:
                s += "O"
        s += "\\\\\n"
    
    print(s)
