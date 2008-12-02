#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.view

class Cleanup:
    """
    This class provides a handler to the Cleanup window view.
    The idea is that it displays a large folder icon with a label like
    "Please Wait...".  Then when it finishes cleaning up, the label will 
    change to "Finished cleaning up /path/to/folder"
    
    """

    def __init__(self):
        self.view = component.view.InterfaceView(self, "Cleanup")

    def on_cleanup_destroy(self, widget):
        gtk.main_quit()

    def on_cleanup_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_cleanup_ok_clicked(self, widget):
        gtk.main_quit()
        
if __name__ == "__main__":
    window = Cleanup()
    gtk.main()
