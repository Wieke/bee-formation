from random import Random

class RandomBee:

    def __init__(self, args):
        self.awake = True
        self.generator = Random(args["seed"])

    def arguments():
        return {"seed" : int}

    def behave(self, perception):
        r = self.generator.random()
        if r < 0.25:
            return (0,1)
        elif r < 0.50:
            return (1,0)
        elif r < 0.75:
            return (0, -1)
        else:
            return (-1,0) 
   
    def name():
        return "Random bee"
