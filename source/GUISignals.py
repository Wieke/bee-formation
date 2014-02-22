import cairo
from gi.repository import Gtk

class GUISignals(object):

    def __init__(self, main, world):
        self.main = main
        self.world = world

    def on_mainwindow_destroy(self, widget):
        """Quit Gtk"""
        Gtk.main_quit()

    def on_world_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""

        if self.world.double_buffer is not None:
            cr.set_source_surface(self.world.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')

        return False

    """CONFIGURATION FUNCTIONS FOR GUI"""
    def on_world_configure_event(self, widget, event, data=None):
        """Configure the double buffer based on size of the widget"""

        # Destroy previous buffer
        if self.world.double_buffer is not None:
            self.world.double_buffer.finish()
            self.world.double_buffer = None

        # Create a new buffer
        self.world.double_buffer = cairo.ImageSurface(\
                cairo.FORMAT_ARGB32,
                widget.get_allocated_width(),
                widget.get_allocated_height()
            )

        # Initialize the buffer
        self.world.draw_something()

        return False

    def on_beeselector_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            entry = model[tree_iter][0]
            
            for bee in self.main.beeclasses:
                if entry == bee.name():
                    self.main.selectedbeeclass = bee
                    
            self.main.logline("Selected %s." % self.main.selectedbeeclass.name())
    
