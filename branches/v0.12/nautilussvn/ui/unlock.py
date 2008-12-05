#!/usr/bin/env python

import pygtk
import gobject
import gtk

import nautilussvn.ui.add

class Unlock(nautilussvn.ui.add.Add):
    def __init__(self):
        nautilussvn.ui.add.Add.__init__(self)
        
        self.window = self.view.get_widget("Add")
        self.window.set_title("Unlock")

if __name__ == "__main__":
    window = Unlock()
    gtk.main()
