from gi.repository import Gtk, Gdk
from os.path import abspath, dirname, join, splitext
from numpy.random import randint
from sys import path
from imp import reload
from os import listdir
from GUISignals import GUISignals
from World import World
from View import View
from gi.repository.GLib import timeout_add_seconds, timeout_add

class BeeForm(object):
    """Double buffer in PyGObject with cairo"""

    def __init__(self):
        self.beearguments = None
        self.argumenttypes = None
        self.amountofbees = 0
        self.widthofworld = 20
        self.heightofworld = 20
        self.worldseed = 1
        self.selectedbeeclass = None
        self.runworldinterval = (1/3)*1000
        self.running = False
        self.beeclasses = None
        self.world = None
        
        # Build GUI
        self.builder = Gtk.Builder()
        self.glade_file = 'glade/main.glade'
        self.builder.add_from_file(self.glade_file)

        # Get objects
        go = self.builder.get_object
        self.window = go('mainwindow')
        self.logbuffer = go('logbuffer')
        self.beedebugbuffer = go('beedebugbuffer')
        self.amountbuffer = go('amountbuffer')
        self.beecomstore = go('beecommunicationstore')
        self.beetypelist = Gtk.ListStore(str)
        self.beeselector = go('beeselector')
        self.argumentstore = go('argumentstore')
        self.argumentlist = go('argumentlist')
        self.comstore = None
        self.comlist = go('communicationlist')
        self.drawarea = go("world")
        self.timelabel = go("time")

        #Add EventMask to drawarea
        self.drawarea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK) 
        
        # Connect signals
        self.view = View(self)
        self.guisignals = GUISignals(self, self.view)
        self.builder.connect_signals(self.guisignals)

        self.drawarea.connect('button-press-event', self.guisignals.on_drawarea_button_press)

        #Set up Bee Selector
        self.log = ''
        self.loadbees()

        for bee in self.beeclasses:
            self.beetypelist.append([bee.name()])

        self.beeselector.set_model(self.beetypelist)
        renderer_text = Gtk.CellRendererText()
        self.beeselector.pack_start(renderer_text, True)
        self.beeselector.add_attribute(renderer_text, "text", 0)

        #Set up Argument List
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

        self.setupcomlist()
        
        # Everything is ready
        self.window.show()
        self.updateDrawingArea()

    def updateamount(self):
        if self.beearguments is not None:
            if "formation" in self.beearguments:
                self.amountofbees = len(self.beearguments["formation"])
                text = str(self.amountofbees)
                buf = self.amountbuffer
                start, end = buf.get_bounds()
                buf.delete(start,end)
                buf.insert(start, text, length=len(text))

    def updateDrawingArea(self):
        self.drawarea.queue_draw()

    def logline(self, text):
        text += "\n"
        self.logbuffer.insert(
            self.logbuffer.get_end_iter(),
            text, length=len(text))

    def exception2str(self, e):
        if e.__class__ is AttributeError:
            return e.args[0]
        s =  "Traceback (most recent call only):\n"
        s += "  File \"" + e.filename + ", line " + str(e.lineno) + "\n"
        s += e.text + " "*(e.offset-1) + "^" + "\n"
        s += e.__class__.__name__ + ": " + e.msg
        return s

    def reloadbees(self):
        if self.selectedbeeclass is not None:
            prev = self.selectedbeeclass.name()
        else:
            prev = None
        
        self.loadbees()
        
        self.beetypelist.clear()

        for bee in self.beeclasses:
            self.beetypelist.append([bee.name()])

        if prev is not None:
            self.selectedbeeclass = next((x for x in self.beeclasses
                            if x.name() == prev), None)

            if self.selectedbeeclass is not None:
                self.beeselector.set_active(
                    [x.name() for x in self.beeclasses].index(
                        prev))
        
        if self.running:
            self.preparetheworld()
    
    def loadbees(self):
        """Reads the /bees/ folder and imports the bees within"""

        if self.beeclasses is None:
            func = __import__
        else:
            func = lambda x: reload(__import__(x))

        names = list(map(lambda x: splitext(x)[0],
                         [ file for file in listdir("bees")
                           if file.endswith(".py")]))
        
        path.append("bees")

        self.beeclasses = []
        
        for name in names:
            try:
                self.beeclasses.append(getattr(func(name),name))
                self.logline("Loaded " + name + ".py")
            except Exception as e:
                self.logline("\nFailed to load " + name + ".py")
                self.logline(self.exception2str(e) + "\n")                


    def preparetheworld(self):
        if self.checkbeearguments():
            self.world = World(self.selectedbeeclass,
                               self.amountofbees,
                               self.widthofworld,
                               self.heightofworld,
                               self.beearguments.copy(),
                               self.worldseed)
            self.view.startworldwidth = self.widthofworld
            self.view.startworldheight = self.heightofworld
            self.view.reset(self.world)
            self.updatetime()
            self.updateDrawingArea()
            self.setupcomlist()


    def startstop(self):
        if self.world is not None:
            if not self.running:
                self.running = True
                timeout_add(self.runworldinterval, self.runWorld)
            else:
                self.running = False

    def stepback(self):
        if self.world is not None:
            if self.world.currentState > 0:            
                self.running = False
                self.world.stepBackward()
                self.updateDrawingArea()
                self.updateComlist()
                self.updatebeedebug()
                self.updatetime()

    def stepforward(self):
        if self.world is not None:
            self.running = False
            self.world.stepForward()
            self.updateDrawingArea()
            self.updateComlist()
            self.updatebeedebug()
            self.updatetime()            

    def updatetime(self):
        text = str(self.world.currentState) + " / " + str(self.world.totalStates)
        self.timelabel.set_text(text)
    
    def setupcomlist(self):
        position = 0

        if self.comlist.get_n_columns() > 0:
            for i in reversed(range(0,self.comlist.get_n_columns())):
                self.comlist.remove_column(
                    self.comlist.get_column(i))

        columns = ["Position","Awake"]

        if self.selectedbeeclass is not None:
            if self.selectedbeeclass.comkeys() is not None:
                columns = columns + self.selectedbeeclass.comkeys()

            
        for c in columns:
            column = Gtk.TreeViewColumn(c)
            cell = Gtk.CellRendererText()
            column.pack_start(cell, True)

            column.add_attribute(cell, "text", position)
            position += 1

            self.comlist.append_column(column)

        self.comstore = Gtk.ListStore(*[str]*position)
        self.comlist.set_model(self.comstore)

    def updateComlist(self):
        self.comstore.clear()
        for position, bee, move, com in self.world.getworldState():
            entry = list()
            entry.append(str(position[0]) + "," + str(position[1]))
            entry.append(str(bee.awake))
            if bee.__class__.comkeys() is not None:
                for c in bee.__class__.comkeys():
                    if com is not None:
                        if c in com:
                            entry.append(str(com[c]))
                        else:
                            entry.append("None")
                    else:
                        entry.append("None")

            self.comstore.append(entry)
            

    def checkbeearguments(self):
        if self.selectedbeeclass == None:
            self.logline("No bee selected")
            return False
    
        if self.amountofbees == None:
            self.logline("Amount of bees not set.")
            return False
        
        elif self.amountofbees < 1 or "formation" not in self.beearguments:
            self.logline("Please draw a formation of at least a single bee")
            return False
            
        if self.widthofworld == None:
            self.logline("Width not set.")
            return False
            
        if self.heightofworld == None:
            self.logline("Height not set.")
            return False
            
        if self.worldseed == None:
            self.logline("Seed of bees not set.")
            return False

        if any(map(lambda x: x == None, self.beearguments.values())):
            self.logline("Not all bee arguments have been set.")
            return False

        return True

    def updatebeedebug(self):
        if self.world is not None:
            state = self.world.getworldState()
            text = "No bee selected."
            if self.view.selectedbee is not None:
                if len(self.view.selectedbee.debugInformation) > 0:
                    text = self.view.selectedbee.debugInformation
                else:
                    text = "No debug info."

            buf = self.beedebugbuffer
            start, end = buf.get_bounds()
            buf.delete(start,end)
            buf.insert(start, text, length=len(text))

    def runWorld(self):
        if self.running:
            if self.world.timeToFinish == None:
                if self.world.currentState == self.world.totalStates:
                    self.world.stepForward()
                    self.updateDrawingArea()
                    self.updateComlist()
                    self.updatebeedebug()
                    self.updatetime()
                timeout_add(self.runworldinterval, self.runWorld)
            else:
                self.startstop()
                self.logline("Finished in " + str(self.world.timeToFinish) + " seconds!\nEnergy consumed: " + str(self.world.beeSteps) + "\nSpace needed: " + str(self.world.sizeOfWorld))

if __name__ == '__main__':
    gui = BeeForm()
    Gtk.main()
