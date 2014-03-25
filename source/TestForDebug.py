import numpy as np
from numpy import array
old = [array([1,2]), array([1,1]), array([2,1]), array([3,5])]
new = [array([1,2]), array([2,1]), array([2,1]), array([3,5])]
moves = [array([0,0]), array([1,0]), array([0,0]), array([0,0])]
import World
a = World.findCollisions(new)
