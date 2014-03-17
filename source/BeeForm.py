from gi.repository import Gtk, Gdk
from os.path import abspath, dirname, join, splitext
from numpy.random import randint
from sys import path
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
        self.runworldinterval = 1
        self.running = False
        self.selectedbeeclass = None
        
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
        self.drawarea = go("world")

        #Add EventMask to drawarea
        self.drawarea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK) 
        
        # Connect signals
        self.view = View(self)
        self.guisignals = GUISignals(self, self.view)
        self.builder.connect_signals(self.guisignals)

        self.drawarea.connect('button-press-event', self.guisignals.on_drawarea_button_press)

        #Set up Bee Selector
        self.log = ''
        self.beeclasses = self.loadbees()

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
        s =  "Traceback (most recent call only):\n"
        s += "  File \"" + e.filename + ", line " + str(e.lineno) + "\n"
        s += e.text + " "*(e.offset-1) + "^" + "\n"
        s += e.__class__.__name__ + ": " + e.msg
        return s

    def reloadbees(self):
        self.beeclasses = self.loadbees()
        
        self.beetypelist.clear()

        for bee in self.beeclasses:
            self.beetypelist.append([bee.name()])

        if self.selectedbeeclass is not None:
            self.selectedbeeclass = next(x for x in self.beeclasses
                            if x.name() == self.selectedbeeclass.name())

            self.beeselector.set_active(
                [x.name() for x in self.beeclasses].index(
                    self.selectedbeeclass.name()))           
        
        if self.running:
            self.preparetheworld()
    
    def loadbees(self):
        """Reads the /bees/ folder and imports the bees within"""

        names = list(map(lambda x: splitext(x)[0],
                         [ file for file in listdir("bees")
                           if file.endswith(".py")]))

        path.append("bees")

        classes = []
        
        for name in names:
            try:
                classes.append(getattr(__import__(name),name))
                self.logline("Loaded " + name + ".py")
            except Exception as e:
                self.logline("\nFailed to load " + name + ".py")
                self.logline(self.exception2str(e) + "\n")                

        return classes

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
            self.updateDrawingArea()
            #self.view.setupcomlist()
            if not self.running:
                self.runWorld()
                self.running = True

    def checkbeearguments(self):
        if self.selectedbeeclass == None:
            self.logline("No bee selected")
            return False
    
        if self.amountofbees == None:
            self.logline("Amount of bees not set.")
            return False
        elif self.amountofbees < 1:
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

    def runWorld(self):
        if self.world.totalStates >= 0:
            """When a user goes back in the history this should be pauze somehow
               e.g. when states are not equal the user is going back in time.
               Disadvantage the max wait is 'runworldinterval' second(s) to contiue
            """
            if self.world.currentState == self.world.totalStates:
                self.world.stepForward()
                self.updateDrawingArea()
            timeout_add_seconds(self.runworldinterval, self.runWorld)
        else:
            self.logline("World is not prepared")

if __name__ == '__main__':
    gui = BeeForm()
    Gtk.main()
