import cairo
from numpy import array, array_equal, around, amin, amax
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
            elif self.main.beearguments is not None:
                if "formation" in self.main.beearguments:
                    f = self.main.beearguments["formation"]

                    if not any(map(lambda x: array_equal(pos,x),f)):
                        f.append(pos)
                    else:
                        del f[list((map(lambda x: array_equal(pos,x),f))).index(True)]
                    
                else:
                    self.main.beearguments["formation"] = list()
                    self.main.beearguments["formation"].append(pos)

                self.main.updateamount()

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

        if self.worldsize is None:
            worldwidth = self.main.widthofworld
            worldheight = self.main.heightofworld
            if self.world is not None:
                worldwidth += 5
                worldheight += 5
            self.originalworldsize = array([worldwidth, worldheight])
        else:
            worldwidth, worldheight = self.originalworldsize
            if state is not None:
                positions, bees, movement, communication = map(list, zip(*state))
                
                func = lambda y,z: y(list(map(lambda x: x[z], positions)))
                w = func(amax,0) - func(amin,0) + 2
                h = func(amax,1) - func(amin,1) + 2
                
                if worldwidth < w:
                    worldwidth = w
                if worldheight < h:
                    worldheight = h               
                         
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
            movement = [array([0,0]) if x==None else x for x in movement]
            positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))
            centerofmass = around(sum(positions)/len(positions))

            func = lambda y,z: y(list(map(lambda x: x[z], positions)))

            centerbees = around(array([(func(amax,0) - func(amin,0))/2 + func(amin,0),
                                       (func(amax,1) - func(amin,1))/2 + func(amin,1)]))
            
            self.offset = center - centerbees 
            
            self.f  = lambda x: (x + 0.5 + self.offset + self.margin)/self.worldsize
            self.fi = lambda x: x*self.worldsize - 0.5 - self.offset - self.margin
            self.gridonly = False
        else:
            self.f  = lambda x: (x + 0.5  + self.margin)/self.worldsize
            self.fi = lambda x: x*self.worldsize - 0.5 - self.margin
            self.gridonly = True

    def updateframe(self, state):
        if state is None:
            return
        
        positions, bees, movement, communication = map(list, zip(*state))
        movement = [array([0,0]) if x==None else x for x in movement]
        width = self.double_buffer.get_width()
        height = self.double_buffer.get_height()
        
        positions = positions + list(map(lambda x: x[0] + x[1], zip(positions, movement)))
        
        x = [x for [x,y] in map(self.f, positions)]
        y = [y for [x,y] in map(self.f, positions)]
        [worldwidth, worldheight] = self.worldsize
        
        if min(x) <= 0 or max(x) >= 1 or min(y) <= 0 or max(y) >= 1:
            if (max(x) - min(x)) >= 1 or (max(y) - min(y)) >= 1:
                worldwidth += 2
                worldheight += 2

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
            
            func = lambda y,z: y(list(map(lambda x: x[z], positions)))
            centerbees = around(array([(func(amax,0) - func(amin,0))/2 + func(amin,0),
                                       (func(amax,1) - func(amin,1))/2 + func(amin,1)]))
            
            self.offset = center - centerbees
            
            self.margin = (self.worldsize - around(self.worldsize - 0.5))/2
            
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
        
        for pos,bee,_,_ in state:
            key = (pos[0],pos[1])
            if key in todraw:
                if bee.awake:
                    todraw[key] = (todraw[key][0],todraw[key][1]+1, todraw[key][2]+1, todraw[key][3])
                else:
                    todraw[key] = (todraw[key][0],todraw[key][1]+1, todraw[key][2], todraw[key][3]+1)                    
            else:
                if bee.awake:
                    todraw[key]  = (pos,1,1,0)
                else:
                    todraw[key]  = (pos,1,0,1)
            
        for pos,nr,awake,sleeping in todraw.values():
            x,y = self.f(pos)

            if nr == 1:
                cc.save()
                cc.translate(x,y)
                cc.scale(1/self.worldsize[0], 1/self.worldsize[1])
                cc.arc(0,0,0.35,0, 2*pi)
                cc.move_to(0,0)
                cc.restore()

                if awake == 1:
                    cc.set_source_rgb(0, 0, 0)
                else:
                    cc.set_source_rgb(0.8, 0.8, 0.8)
                cc.fill()

            if nr > 1:
                cc.save()
                cc.translate(x,y)
                cc.scale(1/self.worldsize[0], 1/self.worldsize[1])
                if sleeping > 0:
                    cc.move_to(0,0)
                    cc.arc(0,0,0.35,0, 2*(awake/(sleeping+awake))*pi)
                    cc.line_to(0,0)
                    cc.set_source_rgb(0, 0, 0)
                    cc.fill()


                    cc.move_to(0,0)
                    cc.arc(0,0,0.35,2*(awake/(sleeping+awake))*pi, 2*pi)
                    cc.line_to(0,0)
                    cc.set_source_rgb(0.8, 0.8, 0.8)
                    cc.fill()
                else:
                    cc.arc(0,0,0.35,0, 2*pi)                    
                    cc.set_source_rgb(0, 0, 0)
                    cc.fill()

                cc.set_font_size(0.6)
                (x, y, width, height, dx, dy) = cc.text_extents(str(nr))
                cc.set_source_rgb(1, 1, 1)
                cc.move_to(-1.2*width/2, height/2)    
                cc.show_text(str(nr))
                cc.restore()
                cc.set_line_width(line_width)

    def drawformation(self, cc):
        line_width, _ = cc.device_to_user(1.0, 0.0)

        if self.main.beearguments is not None:
            if "formation" in self.main.beearguments:                
                for pos in self.main.beearguments["formation"]:
                    x,y = self.f(pos)
                    
                    cc.save()
                    cc.translate(x,y)
                    cc.scale(1/self.worldsize[0], 1/self.worldsize[1])
                    cc.arc(0,0,0.35,0, 2*pi)
                    cc.move_to(0,0)
                    cc.restore()
                    cc.set_line_width(line_width)
                    cc.set_source_rgb(0, 0, 0)
                    cc.stroke()


    def drawmovement(self, cc, state):
        line_width, _ = cc.device_to_user(2.0, 0.0)

            
        for pos,_ , move, _ in state:
            x,y = self.f(pos)

            if move is not None:
                if move[0] != 0 or move[1] != 0:
                
                    cc.save()
                    cc.translate(x,y)
                    cc.scale(1/self.worldsize[0], 1/self.worldsize[1])

                    if array_equal(move, array([-1,0])):
                        cc.rotate(pi)
                    elif array_equal(move, array([0,1])):
                        cc.rotate(0.5*pi)
                    elif array_equal(move, array([0,-1])):
                        cc.rotate(1.5*pi)
                    
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
                self.prevwindowsize = array([width,height])

            state = None
            if self.world is not None:
                state = self.world.getworldState()

            if self.worldsize is None or not array_equal(self.prevwindowsize,array([width,height])):
                self.initiateframe(state)
                self.prevwindowsize = array([width,height])
            #else:
            #    self.updateframe(state)
            
            if state is not None:

                #Update Bee Communication
                #self.updatebeecommunication(state)
                
                #Determene frame of reference
                
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
                self.drawformation(cc)
            # Flush drawing actions
            self.double_buffer.flush()

        else:
            print('Invalid double buffer')
