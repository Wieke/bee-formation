import cairo
from numpy import array
from numpy import around
from math import pi

class View(object):

    def __init__(self, main, world):
        self.main = main
        self.world = world
        self.origin = None

        # Create buffer
        self.double_buffer = None

    def initiateframe(self, positions, movement, width, height):

        positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))

        centerofmass = around(sum(positions)/len(positions))

        #worldwidth = max(self.main.widthofworld,self.main.heightofworld)
        #worldheight = worldwidth

        worldwidth = self.main.widthofworld
        worldheight = self.main.heightofworld
                         
        canvasratio = width / height
        worldratio = worldwidth / worldheight
        print("width="+str(width) + " height=" + str(height))
        diffwidth = 0
        diffheight = 0
        
        
        if worldratio < canvasratio:
            worldwidth = worldheight * canvasratio
            center = around(array([worldwidth - 1, worldheight])/2)
        elif worldratio > canvasratio:
            worldheight = worldwidth / canvasratio
            center = around(array([worldwidth, worldheight - 1])/2)

        square = array([1/worldwidth, 1/worldheight])

        worldsize = array([worldwidth,worldheight])

        margin = (worldsize - around(worldsize - 0.5))/2
        
        offset = center - centerofmass 
        
        f = lambda x: (x + 0.5 + offset + margin)/worldsize
        
        return (f, square, worldwidth, worldheight, margin)

    def drawgrid(self, cc, worldwidth, worldheight, margin):
        for i in range(0, int(worldwidth + 1)):
            cc.move_to((i + margin[0])/worldwidth,0)
            cc.line_to((i + margin[0])/worldwidth,1)
            cc.set_line_width(0.01 / worldwidth)
            cc.set_source_rgb(0, 0, 0)
            cc.stroke()

        for i in range(0, int(worldheight + 1)):
            cc.move_to(0,(i + margin[1])/worldheight)
            cc.line_to(1,(i + margin[1])/worldheight)
            cc.set_line_width(0.01 / worldheight)
            cc.set_source_rgb(0, 0, 0)
            cc.stroke()

    def drawbees(self, cc, bees, f, square):
        line_width, _ = cc.device_to_user(1.0, 0.0)

        for pos in bees:
            x,y = f(pos)
            cc.save()
            cc.translate(x,y)
            cc.scale(square[0],square[1])
            cc.arc(0,0,0.35,0, 2*pi)
            cc.restore()
            cc.set_line_width(line_width)
            cc.set_source_rgb(0, 0, 0)
            cc.fill()           

    def update(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            state = self.world.getworldState()
            
            
            # Create cairo context with double buffer as is DESTINATION
            cc = cairo.Context(db)
            
            # Scale to device coordenates
            width = db.get_width()
            height = db.get_height()
            cc.scale(width, height)

            # Draw a white background
            cc.set_source_rgb(1, 1, 1)
            cc.rectangle(0, 0, 1, 1)
            cc.fill()
            
            if state is not None:
                positions, bees, movement, communication = map(list, zip(*state))
                
                #Determene frame of reference
                f, square, worldwidth, worldheight, margin = self.initiateframe(positions, movement, width, height)
                
                #Draw Grid

                self.drawgrid(cc, worldwidth, worldheight, margin)

                #Draw Bees
                self.drawbees(cc, positions, f, square)
                
                #Draw Movement

                #Draw Communication

                #Draw Debug Info


               
                

                
                



            # Flush drawing actions
            db.flush()

        else:
            print('Invalid double buffer')
