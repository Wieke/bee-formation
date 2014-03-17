import cairo
from numpy import array, array_equal, around
from World import lineofsight
from math import pi, atan
from itertools import product as iterprod

class View(object):

    def __init__(self, main):
        self.main = main
        self.world = None
        self.origin = None
        self.worldsize = None
        self.margin = None
        self.offset = None
        self.prevwindowsize = None
        self.f = None
        self.fi = None
        self.selectedbee = None

        # Create buffer
        self.double_buffer = None

    def clickEvent(self, x,y):
        if self.fi is not None:
            pos = around(self.fi(array([x,y])))
            
            if self.world is not None:
                state = self.world.getworldState()
                if state is not None:
                    self.selectedbee = next((x[1] for x in state if array_equal(x[0],pos)), None)
                    

    def reset(self, world):
        self.world = world
        self.worldsize = None
        self.margin = None
        self.offset = None
        self.selectedbee = None
        self.f = None
        self.fi = None

    def initiateframe(self, state):
        
        width = self.double_buffer.get_width()
        height = self.double_buffer.get_height()

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

        if state is not None:
            positions, bees, movement, communication = map(list, zip(*state))
            positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))
            centerofmass = around(sum(positions)/len(positions))
            
            self.offset = center - centerofmass 
            
            self.f  = lambda x: (x + 0.5 + self.offset + self.margin)/self.worldsize
            self.fi = lambda x: x*self.worldsize - 0.5 - self.offset - self.margin

    def updateframe(self, state):
            positions, bees, movement, communication = map(list, zip(*state))
            
            width = self.double_buffer.get_width()
            height = self.double_buffer.get_height()
            
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

    def drawbees(self, cc, state):
        line_width, _ = cc.device_to_user(1.0, 0.0)

        todraw = dict()
        
        for pos,_,_,_ in state:
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

    def drawmovement(self, cc, state):
        line_width, _ = cc.device_to_user(2.0, 0.0)

            
        for pos,_ , move, _ in state:
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

    def drawselection(self,cc,state):
        if self.selectedbee is not None:
            pos = next((x[0] for x in state if x[1] is self.selectedbee), None)
            
            line_width, _ = cc.device_to_user(1.0, 0.0)
            x,y = self.f(pos)
            
            cc.save()
            cc.translate(x,y)
            cc.scale(1/self.worldsize[0], 1/self.worldsize[1])

            cc.move_to(-0.5,-0.5)
            cc.line_to(0.5,0.5)
            cc.move_to(-0.5,0.5)
            cc.line_to(0.5, -0.5)
            
            cc.restore()
            cc.set_line_width(line_width)
            cc.set_source_rgb(0, 0, 0)
            cc.stroke()

    def drawocclusionshading(self, cc, state):
        if self.selectedbee is not None:
            pos = next((x[0] for x in state if x[1] is self.selectedbee), None)
            positions, bees, movement, communication = map(list, zip(*state))

            xmin,ymin = self.fi(array([0,0]))
            xmax,ymax = self.fi(array([1,1]))

            for square in iterprod(range(int(xmin)-2,int(xmax)+2),
                                        range(int(ymin)-2,int(ymax)+2)):
                square = array(square)

                if not lineofsight(pos, square, positions):
                    x,y = self.f(square)
                    
                    cc.save()
                    cc.translate(x,y)
                    cc.scale(1/self.worldsize[0], 1/self.worldsize[1])

                    cc.rectangle(-0.5,-0.5,1,1)
                    
                    cc.restore()
                    cc.set_source_rgb(0.9, 0.9, 0.9)
                    cc.fill()
        
    def updatebeedebug(self, state):
        text = "No bee selected."
        if self.selectedbee is not None:
            if self.selectedbee.debugInformation is not None:
                text = self.selectedbee.debugInformation
            else:
                text = "No debug info."

        buf = self.main.beedebugbuffer
        start, end = buf.get_bounds()
        buf.delete(start,end)
        buf.insert(start, text, length=len(text))

    def setupcomlist(self):
        column0 = Gtk.TreeViewColumn("Argument")
        column1 = Gtk.TreeViewColumn("Value")
        
        argument = Gtk.CellRendererText()
        value = Gtk.CellRendererText()
        value.props.editable = True
        value.connect("edited", self.guisignals.argument_edited)
    
        column0.pack_start(argument, True)
        column1.pack_start(value, True)

        column0.add_attribute(argument, "text", 0)
        column1.add_attribute(value, "text", 1)

        self.argumentlist.append_column(column0)
        self.argumentlist.append_column(column1)
                
    def update(self):
        """Draw something into the buffer"""
        if self.double_buffer is not None:       
            # Create cairo context with double buffer as is DESTINATION
            cc = cairo.Context(self.double_buffer)
            
            # Scale to device coordenates
            width = self.double_buffer.get_width()
            height = self.double_buffer.get_height()
            cc.scale(width, height)

            # Draw a white background
            cc.set_source_rgb(1, 1, 1)
            cc.rectangle(0, 0, 1, 1)
            cc.fill()

            if self.prevwindowsize is None:
                self.prevwindowsize = (width,height)

            if self.worldsize is None or self.prevwindowsize != (width,height):
               self.initiateframe(None)
            
            if self.world is not None:
                state = self.world.getworldState()
                if state is not None:

                    #Update Bee Debug
                    self.updatebeedebug(state)

                    #Update Bee Communication
                    #self.updatebeecommunication(state)
                    
                    #Determene frame of reference

                    
                    if self.f is None or self.prevwindowsize != (width,height):
                        self.initiateframe(state)
                    else:
                        self.updateframe(state)
                    
                    #Draw occlusion shading
                    if self.world.constraints["occlusion"]:
                        self.drawocclusionshading(cc,state)
                    
                    #Draw Grid
                    self.drawgrid(cc)

                    #Draw Bees
                    self.drawbees(cc, state)
                    
                    #Draw Movement
                    self.drawmovement(cc, state)

                    #Draw selection
                    self.drawselection(cc, state)
                    
                    #Draw Communication

                    #Draw Debug Info
            else:
                self.drawgrid(cc)
            # Flush drawing actions
            self.double_buffer.flush()

        else:
            print('Invalid double buffer')
