#!/usr/bin/env python

import pygtk
import gobject
import gtk
import gtk.glade

class InterfaceView:
    def __init__(self, callback_obj, filename, id):
        path = "glade/%s.glade" % filename        
        self.tree = gtk.glade.XML(path, id)
        self.tree.signal_autoconnect(callback_obj)
        self.id = id
        
    def get_widget(self, id):
        return self.tree.get_widget(id)
        
    def hide(self):
        self.tree.get_widget(self.id).set_property('visible', False)
        
    def show(self):
        self.tree.get_widget(self.id).set_property('visible', True)
