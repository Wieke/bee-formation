from gi.repository import Gtk
from os.path import abspath, dirname, join, splitext
from sys import path
import os
from GUISignals import GUISignals
from World import World

class BeeForm(object):
    """Double buffer in PyGObject with cairo"""

    def __init__(self):        
        # Build GUI
        self.builder = Gtk.Builder()
        self.glade_file = 'glade/main.glade'
        self.builder.add_from_file(self.glade_file)

        # Get objects
        go = self.builder.get_object
        self.window = go('mainwindow')
        self.logbuffer = go('logbuffer')
        self.beetypelist = Gtk.ListStore(str)
        self.beeselector = go('beeselector')
        self.argumentstore = go('argumentstore')

        #import code
        #code.InteractiveConsole(locals=locals()).interact()
        
        # Connect signals
        self.world = World(self)
        self.guisignals = GUISignals(self, self.world)
        self.builder.connect_signals(self.guisignals)

        #Set up things
        self.log = ''
        self.beeclasses = self.loadbees()
        self.selectedbeeclass = None

        for bee in self.beeclasses:
            self.beetypelist.append([bee.name()])

        self.beeselector.set_model(self.beetypelist)
        renderer_text = Gtk.CellRendererText()
        self.beeselector.pack_start(renderer_text, True)
        self.beeselector.add_attribute(renderer_text, "text", 0)
        
        # Everything is ready
        self.window.show()

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
    
    def loadbees(self):
        """Reads the /bees/ folder and imports the bees within"""

        names = list(map(lambda x: splitext(x)[0],
                         [ file for file in os.listdir("bees")
                           if file.endswith(".py")]))

        path.append("bees")

        modules = []
        
        for name in names:
            try:
                modules.append(__import__(name))
                self.logline("Loaded " + name + ".py")
            except Exception as e:
                self.logline("\n" + self.exception2str(e) + "\n")
            
        classes = list(map(lambda z: getattr(z[0],z[1]),
                           zip(modules, names)))

        return classes


if __name__ == '__main__':
    gui = BeeForm()
    Gtk.main()
