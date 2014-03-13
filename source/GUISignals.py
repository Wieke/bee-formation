import cairo
from gi.repository import Gtk

class GUISignals(object):

    def __init__(self, main, view):
        self.main = main
        self.view = view

    def on_mainwindow_destroy(self, widget):
        """Quit Gtk"""
        Gtk.main_quit()

    def on_InitializeButton_clicked(self, widget):
        """Initialize world"""
        self.main.preparetheworld()

    def on_AmountEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.amountofbees = x

    def on_XRangeEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.widthofworld = x

    def on_YRangeEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.heightofworld = x
            
    def on_SeedEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.seedofbees = x
            
    def on_world_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""

        if self.view.double_buffer is not None:
            cr.set_source_surface(self.view.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')

        return False

    """CONFIGURATION FUNCTIONS FOR GUI"""
    def on_world_configure_event(self, widget, event, data=None):
        """Configure the double buffer based on size of the widget"""

        # Destroy previous buffer
        if self.view.double_buffer is not None:
            self.view.double_buffer.finish()
            self.view.double_buffer = None

        # Create a new buffer
        self.view.double_buffer = cairo.ImageSurface(\
                cairo.FORMAT_ARGB32,
                widget.get_allocated_width(),
                widget.get_allocated_height()
            )

        # Initialize the buffer
        self.view.draw_something()

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

        self.main.beearguments = self.main.selectedbeeclass.arguments()
        self.main.argumentstore.clear()
        self.main.argumenttypes = []
        
        if self.main.beearguments != None:
            for key, value in self.main.beearguments.items():
                self.main.argumentstore.append([key + " (" + value.__name__ + ")"
                                                , ""])
                self.main.argumenttypes.append(value)
                self.main.beearguments[key] = None
                
        

    def argument_edited(self, widget, path, text):
        key = self.main.argumentstore[path][0][:-1*len(" (" +
                    self.main.argumenttypes[int(path)].__name__ + ")")]
        t = self.main.argumenttypes[int(path)]

        if len(text) > 0:
            try:        
                if t == str:
                    self.main.beearguments[key] = text
                    self.main.argumentstore[path][1] = text
                elif t == int:
                    self.main.beearguments[key] = int(text)
                    self.main.argumentstore[path][1] = text
                elif t == float:
                    self.main.beearguments[key] = float(text)
                    self.main.argumentstore[path][1] = text
                elif t == bool:
                    if text == "0" or text == "1":
                        self.main.beearguments[key] = bool(text)
                        self.main.argumentstore[path][1] = text
                    else:
                        self.main.logline("\nBoolean values should be entered as either 0 or 1.\n")

                
            except ValueError as e:
                self.main.logline("\n" + e.args[0] + "\n")

    def parseInt(self, text):
        if len(text) > 0:
            try:
                return int(text)
            except ValueError as e:
                self.main.logline("\n" + e.args[0] + "\n")
                return None
                            
