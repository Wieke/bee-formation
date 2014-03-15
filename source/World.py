import cairo
from random import *
import itertools
import numpy as np

class World(object):

    def __init__(self, beeType, numberOfBees, width, height, args, worldseed):
        self.beeType = None
        self.numberOfBees = None
        self.contraints = None
        self.worldStates = None
        self.totalStates = -1
        self.currentState = -1
        self.worldGenerator = None

        #Parameters that need to be looked at
        self.sleepRate = 0.1
        self.sleepLimit = 10

        #possible counterclockwise rotations 0, 90, 180, 270 gegrees
        self.possibleRotations = {0: np.array([[1,0],[0,1]]), 1:
        np.array([[0,-1],[1,0]]),
         2: np.array([[-1,0],[0,-1]]), 3: np.array([[0,1],[-1,0]])}
        
        self.beeType = beeType
        self.numberOfBees = numberOfBees
        self.worldGenerator = Random(worldseed)
        
        #Set constraints dict("occlusion", "collision", "comrange")
        self.constraints = beeType.worldConstraints()

        #assign every bee a random location in the grid
        beeLocations = []
        beePossibleLocations = list(itertools.product(range(1,width),range(1,height)))
        for _ in range(numberOfBees):
            location = self.worldGenerator.choice(beePossibleLocations)
            beePossibleLocations.remove(location)
            beeLocations.append(np.array(location))

        #create the specified number of bee instances
        listOfBees = []
        for _ in range(numberOfBees):
            args["seed"] = Random(args["seed"]).random()
            args["transformation"] = self.possibleRotations[self.worldGenerator.randint(0,3)]
            args["owncoordinates"] = np.array([0,0])
            listOfBees.append(self.beeType(args))

        #Set the global movement of every bee to zero
        globalMovement = [np.array([0,0])] * numberOfBees

        #Set every short range communication of every bee to None
        shortRangeCom = [None] * numberOfBees

        #Create the worldstate at t = 0
        self.worldStates = [list(zip(beeLocations,listOfBees,globalMovement,shortRangeCom))]
        self.totalStates += 1
        self.currentState += 1
          
    def stepForward(self):
        #If state is not in the present move the current state one step closer to the present
        if self.currentState < self.totalStates:
            self.currentState += 1
        #Else generate a new state
        else:
            print("Actually Stepping")
            #Retrieve old state
            states = list(zip(*self.worldStates[self.currentState]))
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
                    if self.worldGenerator.randint(1,10) <= int(self.sleepRate*10):
                        bee.awake = False
                        bee.sleepCounter = self.worldGenerator.randint(1,self.sleepLimit)

                #In any case the bee will execute a behavior (if sleeping => minus 1 on the sleep counter)    
                (beeMovement, newShortRangeCom) = bee.behave(self._perception(locations, shortRangeComs, index, bee))
                move = np.dot(beeMovement, bee.transformation) #From local to global - transformation on the right side
                globalMovement.append(move)
                newLocations.append(locations[index] + move)
                newShortRangeComs.append(newShortRangeCom)

                #When collision is an issue a sequential update is needed. In other words: the current bee needs information of the most up-to-date positions
                if self.constraints["collision"]:
                    locations[index] = locations[index] + globalMovement[index]
                index += 1

            #Add the new state to the list of states
            self.worldStates.append(list(zip(newLocations,bees,globalMovement,newShortRangeComs)))       
            self.totalStates += 1
            self.currentState += 1

    def stepBackward(self):
        if self.currentState <= 0:
            raise IlligalStateException(-1, self.totalStates)
        else:
            self.currentState -= 1
    
    def goToState(self, stateNumber):
        if stateNumber > self.totalStates or stateNumber < 0:
            raise IlligalStateException(stateNumber, self.totalStates)
        else:
            self.currentState = stateNumber    

    def getworldState(self):
        if self.worldStates is None:
            return None
        else:
            return self.worldStates[self.currentState]

    def _perception(self, locations, shortRangeComs, index, bee):
        ownLocation = locations[index]
        otherLocations = locations[:index] + locations[(index + 1):]
        othershortRangeComs = shortRangeComs[:index] + shortRangeComs[(index + 1):]

        accesLocations = []
        if self.constraints["occlusion"]:
            #With occlusion only not blocked agents can be seen
            for otherLoc in otherLocations:
                if self.lineofsight(ownLocation, otherLoc, otherLocations):
                    #from global to local:
                    #1. set the origin to this agent (otherLoc-ownLocation)
                    #2. rotate by np.dot with the transformation matrix on the left side
                    #3. correct for local origin + Bee.ownCoordinates
                    accesLocations.append(np.dot(bee.transformation,(otherLoc-ownLocation))+bee.ownCoordinates)

        else:
            #Without occlusion all the other agents can be seen
            accesLocations = list(map(lambda a: np.dot(bee.transformation,(a-ownLocation))+bee.ownCoordinates , otherLocations))

        accesShortRangeComs = self._accesableShortRangeCommunication(ownLocation,otherLocations, othershortRangeComs, bee) 
        
        return (accesLocations, accesShortRangeComs)

    def linfunc(p1,p2):
        x1, y1 = p1
        x2, y2 = p2

        m = (y2 - y1)/(x2 - x1)
        b = y1 - m*x1

        return lambda x: m*x+b

    def lineofsight(p1, p2, positions):
        f1 = self.linfunc(p1,p2)
        f2 = self.linfunc(p2,p1)
        x1, y1 = p1
        x2, y2 = p2

        for x in range(x1, x2):
            y = f1(x)

            if any(map(lambda x: x == [x,int(y)], positions)):
                return False

            if (y - int(y)) != 0:
                if any(map(lambda x: x== [x, int(y+0.5)], positions)):
                    return False

        for y in range(y1, y2):
            x = f2(y)

            if any(map(lambda x: x == [int(x),y], positions)):
                return False

            if (x - int(x)) != 0:
                if any(map(lambda x: x== [int(x + 0.5), y], positions)):
                    return False
        return True

    def _accesableShortRangeCommunication(self, ownLocation, otherLocations, othershortRangeComs, bee):
        accesShortRangeComs = []
        if self.constraints["comrange"] == 0:
            for index in [i for i, x in enumerate(otherLocations) if np.array_equal(ownLocation,x)]:
                    #from global to local:
                    #1. set the origin to this agent (otherLoc-ownLocation)
                    #2. rotate by np.dot with the transformation matrix on the left side
                    #3. correct for local origin + Bee.ownCoordinates
                accesShortRangeComs.append((np.dot(bee.transformation,(otherLocations[index]-ownLocation))+bee.ownCoordinates, othershortRangeComs[index]))
                
        elif self.constraints["comrange"] == 1:
            neighboringFields = np.array(list(itertools.starmap(lambda a,b: (ownLocation[0]+a, ownLocation[1]+b), itertools.product((0,-1,+1), (0,-1,+1)))))
            neighboringFields = np.split(neighboringFields, len(neighboringFields))
            index = []
            for field in neighboringFields:
                index.append([i for i, x in enumerate(otherLocations) if np.array_equal(field.flatten(),x)])
            index = [item for sublist in index for item in sublist]
            for i in index:
                accesShortRangeComs.append((np.dot(bee.transformation,(otherLocations[i]-ownLocation))+bee.ownCoordinates, othershortRangeComs[i]))
        else:
            #No implementation for more that range of 1 (since it supposed to be short range). A more general method should be developed.
            accesShortRangeComs = list(zip(list(map(lambda x: np.dot(bee.transformation,(x-ownLocation))+bee.ownCoordinates, otherLocations)), othershortRangeComs))

        return accesShortRangeComs
        
class IlligalStateException(Exception):
    def __init__(self, enteredState, totalNumberStates):
        self.enteredState = enteredState
        self.totalNumberStates = totalNumberStates
    def __str__(self):
        return "Given state: " + repr(self.enteredState) + " is illigal. Has to be an integer between 0 and " + repr(self.totalNumberStates)    
