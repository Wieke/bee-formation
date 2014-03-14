import cairo
from random import *
import itertools
import numpy as np

class World(object):

    def __init__(self, main):
        self.main = main
        self.beeType = None
        self.numberOfBees = None
        self.contraints = None
        self.worldState = None

        #possible counterclockwise rotations 0, 90, 180, 270 gegrees
        self.possibleRotations = {0: np.array([[1,0],[0,1]]), 1:
        np.array([[0,-1],[1,0]]),
         2: np.array([[-1,0],[0,-1]]), 3: np.array([[0,1],[-1,0]])}

    def prepare(self, beeType, numberOfBees, width, height, args, worldseed):
        self.beeType = beeType
        self.numberOfBees = numberOfBees

        #Set constraints dict("occlusion", "occlusion", "comrange")
        self.constraints = beeType.worldConstraints()

        #create the specified number of bee instances
        listOfBees = []
        generator = random.Random(args["seed"])
        for _ in range(numberOfBees):
            args["seed"] = generator.random()
            args["transformation"] = self.possibleRotations[random.randint(0,3)]
            listOfBees.append(self.beeType(args))

        #assign every bee a random location in the grid
        beeLocations = []
        beePossibleLocations = list(itertools.product(range(1,width),range(1,height)))
        generator = random.Random(worldseed)
        for _ in range(numberOfBees):
            location = generator.choice(beePossibleLocations)
            beePossibleLocations.remove(location)
            beeLocations.append(np.array(location))

        #Set the global movement of every bee to zero
        globalMovement = [np.array([0,0])] * numberOfBees

        #Set every short range communication of every bee to None
        shortRangeCom = [None] * numberOfBees

        #Create the wordstate at t = 0
        self.worldState = list(zip(beeLocations,listOfBees,globalMovement,shortRangeCom))
          
    def step(self):
        """ A loop needs to execute this function to advance the world one step e.g. by BeeForm."""

        """ Iterate over every bee
              Execture behave
              Update the worldState

        beeMoves = []
        shortComs = []
        #Iteratere over every bee
        for beeState in wordState:
            (location, bee, globalMovement, shortRangeCom) = 
            (beeMove, shortComs) = bee.behave(perception())
            beeMoves.append(beeMoves)
            shortComs.append(shortComs)
        """

            
