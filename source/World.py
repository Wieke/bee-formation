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
        self.totalStates = 0
        self.currentState = 0

        #Parameters that need to be looked at
        self.sleepRate = 0.1
        self.sleepLimit = 10

        #possible counterclockwise rotations 0, 90, 180, 270 gegrees
        self.possibleRotations = {0: np.array([[1,0],[0,1]]), 1:
        np.array([[0,-1],[1,0]]),
         2: np.array([[-1,0],[0,-1]]), 3: np.array([[0,1],[-1,0]])}

    def prepare(self, beeType, numberOfBees, width, height, args, worldseed):
        self.beeType = beeType
        self.numberOfBees = numberOfBees

        #Set constraints dict("occlusion", "collision", "comrange")
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
        self.totalStates = 1
        self.currentState = 1
          
    def stepForward(self):
        #If state is not in the present move the current state one step closer to the present
        if self.currentState < self.totalStates:
            self.currentState += 1
        #Else generate a new state
        else:
            #Retrieve old state
            states = list(zip(*self.wordState[currentState]))
            locations = list(states[0])
            bees = list(states[1])
            shortRangeComs = statesbeeState = list(states[3])

            #Set elements for new state
            globalMovement = []
            newShortRangeComs = []
            newLocations = []

            #Let every bee behave
            index=0
            for bee in bees:
                #if a bee is awake there is a probability (self.sleepRate) that it will be forced to sleep. It will sleep for self.sleepLimit time steps
                if bee.awake:
                    if generator.randint(1,10) <= int(self.sleepRate*10):
                        bee.awake = False
                        bee.sleepCounter = generator.randint(1,self.sleepLimit)

                #In any case the bee will execute a behavior (if sleeping => minus 1 on the sleep counter)    
                (beeMovement, newShortRangeCom) = bee.behave(_perception(locations, shortRangeComs, index))
                move = np.dot(np.transpose(bee.transformation), beeMovement)
                globalMovement.append(move)
                newLocations.append(locations[index] + move)
                newShortRangeComs.append(newShortRangeCom)

                #When collision is an issue a sequential update is needed. In other words: the current bee needs information of the most up-to-date positions
                if self.constraints["collision"]:
                    locations[index] = locations[index] + globalMovement[index]
                index += 1

            #Add the new state to the list of states
            self.worldState.append(list(zip(newLocations,bees,globalMovement,newShortRangeComs)))       
            self.totalStates += 1
            self.currentState += 1

    def stepBackward(self):
        if self.currentState <= 1:
            raise IlligalStateException(0, self.totalStates)
        else:
            self.currentState -= 1
    
    def goToState(self, stateNumber):
        if stateNumber > self.totalStates or stateNumber <= 0:
            raise IlligalStateException(stateNumber, self.totalStates)
        else:
            self.currentState = stateNumber    

    def getWorldState(self):
        return self.worldState[currentState]

    def _perception(self, locations, shortRangeComs, index):
        ownLocation = locations[index]
        otherLocations = locations[:index] + locations[(index + 1):]
        othershortRangeComs = shortRangeComs[:index] + shortRangeComs[(index + 1):]
        
        if self.constraints["occlusion"]:
            #With occlusion only not blocked agents can be seen
            accesLocations = [] #_FUNCTIEWIEKE(ownLocation, otherLocations)
        else:
            #Without occlusion all the other agents can be seen
            accesLocations = otherLocations

        accesShortRangeComs = _accesableShortRangeCommunication(ownLocation,otherLocations, othershortRangeComs) 
        
        return (accesLocations, accesShortRangeComs)

    def _accesableShortRangeCommunication(self, ownLocation, otherLocations, othershortRangeComs):
        accesShortRangeComs = []
        if self.constraints["comrange"] == 0:
            neighborIndex = [i for i, x in enumerate(otherLocations) if np.array_equal(ownLocation,x)]
            return [othershortRangeComs[i] for i in neighborIndex]
                
        else:
            neighboringFields = n.array(list(starmap(lambda a,b: (ownLocation[0]+a, mownLocation[0]+b), product((0,-1,+1), (0,-1,+1)))))
            neighboringFields = n.split(neighboringFields, len(neighboringFields))
            #NOTFINISHED
            
        return shortRangeComs
        
class IlligalStateException(Exception):
    def __init__(self, enteredState, totalNumberStates):
        self.enteredState = enteredState
        self.totalNumberStates = totalNumberStates
    def __str__(self):
        return "Given state: " + repr(self.enteredStatevalue) + " is illigal. Has to be an integer between 1 and " + repr(totalNumberStates)    
