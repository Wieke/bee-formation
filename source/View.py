import cairo
from numpy import array
from numpy import around
from math import pi, atan

class View(object):

    def __init__(self, main, world):
        self.main = main
        self.world = world
        self.origin = None
        self.worldsize = None
        self.margin = None
        self.offset = None
        self.prevwindowsize = None
        self.f = None
        self.fi = None

        # Create buffer
        self.double_buffer = None

    def clickEvent(self, x,y):
        if self.fi is not None:
            pos = around(self.fi(array([x,y])))
            
            print(post)

            if self.view is not None:
                if self.view.get

            

    def reset(self):
        self.worldsize = None
        self.margin = None
        self.offset = None

    def initiateframe(self, positions, movement, width, height):

        positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))

        centerofmass = around(sum(positions)/len(positions))

        worldwidth = self.main.widthofworld
        worldheight = self.main.heightofworld
                         
        canvasratio = width / height
        worldratio = worldwidth / worldheight
        
        if worldratio < canvasratio:
            worldwidth = worldheight * canvasratio
            center = around(array([worldwidth - 1, worldheight])/2)
        elif worldratio > canvasratio:
            worldheight = worldwidth / canvasratio
            center = around(array([worldwidth, worldheight - 1])/2)

        self.worldsize = array([worldwidth,worldheight])

        self.margin = (self.worldsize - around(self.worldsize - 0.5))/2
        
        self.offset = center - centerofmass 
        
        self.f  = lambda x: (x + 0.5 + self.offset + self.margin)/self.worldsize
        self.fi = lambda x: x*self.worldsize - 0.5 - self.offset - self.margin

    def updateframe(self, positions, movement, width, height):
            positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))
            
            x = [x for [x,y] in map(self.f, positions)]
            y = [y for [x,y] in map(self.f, positions)]
            
            if min(x) < 0 or max(x) > 1 or min(y) < 0 or max(y) > 1:

                if ((max(x) - min(x)) >= 1) or ((max(y) - min(y)) >= 1):
                    self.worldsize = self.worldsize + 2

                [worldwidth, worldheight] = self.worldsize
            
                canvasratio = width / height
                worldratio = worldwidth / worldheight

                center = around(array([worldwidth, worldheight])/2)
                
                if worldratio < canvasratio:
                    worldwidth = worldheight * canvasratio
                    center = around(array([worldwidth - 1, worldheight])/2)
                elif worldratio > canvasratio:
                    worldheight = worldwidth / canvasratio
                    center = around(array([worldwidth, worldheight - 1])/2)

                self.worldsize = array([worldwidth,worldheight])
                
                centerofmass = around(sum(positions)/len(positions))
                
                self.margin = (self.worldsize - around(self.worldsize - 0.5))/2
                
                self.offset = center - centerofmass 
                
                self.f = lambda x: (x + 0.5 + self.offset + self.margin)/self.worldsize
                self.fi = lambda x: x*self.worldsize - 0.5 - self.offset - self.margin
        

    def drawgrid(self, cc):
        for i in range(0, int(self.worldsize[0] + 1)):
            cc.move_to((i + self.margin[0])/self.worldsize[0],0)
            cc.line_to((i + self.margin[0])/self.worldsize[0],1)
            cc.set_line_width(0.01 / self.worldsize[0])
            cc.set_source_rgb(0, 0, 0)
            cc.stroke()

        for i in range(0, int(self.worldsize[1] + 1)):
            cc.move_to(0,(i + self.margin[1])/self.worldsize[1])
            cc.line_to(1,(i + self.margin[1])/self.worldsize[1])
            cc.set_line_width(0.01 / self.worldsize[1])
            cc.set_source_rgb(0, 0, 0)
            cc.stroke()

    def drawbees(self, cc, bees):
        line_width, _ = cc.device_to_user(1.0, 0.0)

        todraw = dict()
        
        for pos in bees:
            key = (pos[0],pos[1])
            if key in todraw:
                todraw[key] = (todraw[key][0],todraw[key][1]+1)
            else:
                todraw[key]  = (pos,1)
            
        for pos,nr in todraw.values():
            x,y = self.f(pos)
            
            cc.save()
            cc.translate(x,y)
            cc.scale(1/self.worldsize[0], 1/self.worldsize[1])
            cc.arc(0,0,0.35,0, 2*pi)
            cc.move_to(0,0)
            cc.restore()
            cc.set_line_width(line_width)
            cc.set_source_rgb(0, 0, 0)
            cc.fill()

            if nr > 1:
                cc.save()
                cc.translate(x,y)
                cc.scale(1/self.worldsize[0], 1/self.worldsize[1])
                cc.set_font_size(0.6)
                (x, y, width, height, dx, dy) = cc.text_extents(str(nr))
                cc.set_source_rgb(1, 1, 1)
                cc.move_to(-1.2*width/2, height/2)    
                cc.show_text(str(nr))
                cc.restore()
                cc.set_line_width(line_width)

    def drawmovement(self, cc, positions, movement):
        line_width, _ = cc.device_to_user(2.0, 0.0)

            
        for pos,move in zip(positions,movement):
            x,y = self.f(pos)

            if move[0] != 0 and move[1] != 0:
            
                cc.save()
                cc.translate(x,y)
                cc.scale(1/self.worldsize[0], 1/self.worldsize[1])

                cc.rotate(atan(move[1]/move[0]))
                cc.move_to(0,0)
                cc.line_to(1,0)

                cc.move_to(1,0)
                cc.line_to(0.7, 0.13)

                cc.move_to(1,0)
                cc.line_to(0.7, -0.13)

                cc.restore()
                cc.set_line_width(line_width)
                cc.set_source_rgb(0, 0, 0)
                cc.stroke()

                
    def update(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            state = self.world.worldState
            
            
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
                if self.worldsize is None:
                    self.initiateframe(positions, movement, width, height)
                else:
                    self.updateframe(positions, movement, width, height)
                
                #Draw Grid
                self.drawgrid(cc)

                #Draw Bees
                self.drawbees(cc, positions)
                
                #Draw Movement
                self.drawmovement(cc, positions, movement)

                #Draw Communication

                #Draw Debug Info

            # Flush drawing actions
            db.flush()

        else:
            print('Invalid double buffer')
