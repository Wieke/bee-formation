import cairo
from gi.repository import Gtk
from os.path import abspath, dirname, join, splitext
from sys import path
import os
from GUISignals import GUISignals

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
        
        # Create buffer
        self.double_buffer = None

        # Connect signals
        self.guisignals = GUISignals(self)
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
        

    def draw_something(self):
        """Draw something into the buffer"""
        db = self.double_buffer
        if db is not None:
            # Create cairo context with double buffer as is DESTINATION
            cc = cairo.Context(db)

            # Scale to device coordenates
            cc.scale(db.get_width(), db.get_height())

            # Draw a white background
            cc.set_source_rgb(1, 1, 1)

            # Draw something, in this case a matrix
            rows = 10
            columns = 10
            cell_size = 1.0 / rows
            line_width = 1.0
            line_width, notused = cc.device_to_user(line_width, 0.0)

            for i in range(rows):
                for j in range(columns):
                    cc.rectangle(j * cell_size, i * cell_size, cell_size, cell_size)
                    cc.set_line_width(line_width)
                    cc.set_source_rgb(0, 0, 0)
                    cc.stroke()

            # Flush drawing actions
            db.flush()

        else:
            print('Invalid double buffer')

if __name__ == '__main__':
    gui = BeeForm()
    Gtk.main()
