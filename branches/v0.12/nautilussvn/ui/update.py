#!/usr/bin/env python

import pygtk
import gobject
import gtk

import notification

class Update:
    """
    This class provides an interface to generate an "update".
    Pass it a local path and it will start the update,
    and it will run the notification dialog.  There is no glade view for this
    class.
    
    """

    def __init__(self):
        self.notification = notification.Notification()
        
if __name__ == "__main__":
    window = Update()
    gtk.main()
