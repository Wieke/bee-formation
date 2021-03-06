import cairo
from gi.repository import Gtk

class GUISignals(object):

    def __init__(self, main, view):
        self.main = main
        self.view = view

    def on_reloadbees_clicked(self, widget):
        self.main.reloadbees()

    def on_drawarea_button_press(self, widget, event):
        self.view.clickEvent(event.x/widget.get_allocated_width(),
                             event.y/widget.get_allocated_height())
        self.main.updateDrawingArea()
        self.main.updatebeedebug()

    def on_mainwindow_destroy(self, widget):
        """Quit Gtk"""
        Gtk.main_quit()

    def on_BackButton_clicked(self, widget):
        self.main.stepback()

    def on_PlayButton_clicked(self, widget):
        self.main.startstop()

    def on_ForwardButton_clicked(self, widget):
        self.main.stepforward()    

    def on_InitializeButton_clicked(self, widget):
        """Initialize world"""
        self.main.preparetheworld()        

    def on_XRangeEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.widthofworld = x
        else:
            self.main.widthofworld = 20
        self.main.updateDrawingArea()

    def on_YRangeEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.heightofworld = x
        else:
            self.main.heightofworld = 20
            self.main.updateDrawingArea()
            
    def on_SeedEntry_changed(self, widget):
        """Initialize world"""
        x = self.parseInt(widget.get_text())
        if x != None:
            self.main.worldseed = x
        else:
            self.main.worldseed = 1
            
    def on_world_draw(self, widget, cr):
        """Throw double buffer into widget drawable"""

        if self.view.double_buffer is not None:
            self.view.update()
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
        self.view.update()

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

        if self.main.selectedbeeclass is not None:
            args = self.main.selectedbeeclass.arguments()
            
            if self.main.beearguments is not None:
                new = self.main.selectedbeeclass.arguments()
                for k in new.keys():
                    if k in self.main.beearguments:
                        oldvalue = self.main.beearguments[k]

                        if type(oldvalue) == args[k]:
                            new[k] = oldvalue
                        else:
                            new[k] = None
                    else:
                        new[k] = None
                if "formation" in self.main.beearguments:
                    new["formation"] = self.main.beearguments["formation"]
                self.main.beearguments = new
            else:
                self.main.beearguments = self.main.selectedbeeclass.arguments()
                for k in self.main.beearguments.keys():
                    self.main.beearguments[k] = None


            self.main.argumentstore.clear()
            self.main.argumenttypes = []
            
            if self.main.beearguments != None:
                for key, value in self.main.beearguments.items():
                    if key != "formation":
                        if value is None:
                            t = ""
                        else:
                            t = str(value)
                            
                        self.main.argumentstore.append([key + " (" + args[key].__name__ + ")"
                                                        , t])
                        self.main.argumenttypes.append(args[key])
                        self.main.beearguments[key] = value
                
        

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
                            
