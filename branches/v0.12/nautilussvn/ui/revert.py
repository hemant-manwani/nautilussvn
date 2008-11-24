#!/usr/bin/env python

import pygtk
import gobject
import gtk

import add

class Revert(add.Add):
    def __init__(self):
        add.Add.__init__(self)
        
        self.window = self.view.get_widget("Add")
        self.window.set_title("Revert")
        
if __name__ == "__main__":
    window = Revert()
    gtk.main()
