from random import Random

class BaseBee:
    #Static methods
    def worldConstraints():
        """Return the world settings
             - Occlusion: boolean
             - Collision: boolean
             - shortRange: binairy int
        """
        raise NotImplementedError("Please Implement this method")

    def name():
        """Return name of the type of bee"""
        raise NotImplementedError("Please Implement this method")

    def arguments():
        return {"seed": int}

    #Non-static methods
    def __init__(self, args):
        """awake = Boolean that indicates if an agents is awake or not"""
        self.awake = True

        """Transformation matrix to transform the global coordinate system to the local coordiante system"""
        self.transformation = args["transformation"]

        """Seed for randomness"""
        self.generator = Random(args["seed"])

        """String that contains debug information""" 
        self.debugInformation = None    

    def behave(self, perception):
        """Return (Numpy.Array([xmovement, ymovement]), Dict(shortRangeComm))"""
        raise NotImplementedError("Please Implement this method")
        
