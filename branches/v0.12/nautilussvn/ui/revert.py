#!/usr/bin/env python

import pygtk
import gobject
import gtk

import nautilussvn.ui.add

class Revert(nautilussvn.ui.add.Add):
    def __init__(self):
        nautilussvn.ui.add.Add.__init__(self)
        
        self.window = self.view.get_widget("Add")
        self.window.set_title("Revert")
        
        self.view.get_widget("frame_label").set_label(
            "Files to remove (double-click to view diff) "
        )
        
if __name__ == "__main__":
    window = Revert()
    gtk.main()
