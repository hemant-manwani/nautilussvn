#!/usr/bin/env python

import pygtk
import gobject
import gtk
import gtk.glade

class InterfaceView:
    def __init__(self, callback_obj, id):
        self.tree = gtk.glade.XML("glade/interface.glade", id)
        self.tree.signal_autoconnect(callback_obj)
        
    def get_widget(self, id):
        return self.tree.get_widget(id)
