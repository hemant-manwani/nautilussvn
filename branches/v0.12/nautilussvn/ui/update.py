#!/usr/bin/env python

import pygtk
import gobject
import gtk

import notification

class Update:
    """
    This class provides an interface to generate an "update".
    Pass it a path and it will start an update, running the notification dialog.  
    There is no glade view.
    
    """

    def __init__(self):
        self.notification = notification.Notification()
        
if __name__ == "__main__":
    window = Update()
    gtk.main()
