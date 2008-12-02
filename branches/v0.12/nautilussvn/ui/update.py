#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget

import log
import notification

class Update:
    """
    This class provides an interface to generate an "update".
    Pass it a path and it will start an update, running the notification dialog.  
    There is no glade view.
    
    """

    def __init__(self):
        self.notification = notification.Notification()


class UpdateToRevision:
    """
    This class provides an interface to update a working copy to a specific
    revision.  It has a glade view.
    
    """
    
    DEPTHS = {
        'a': 'Working Copy',
        'b': 'Fully recursive',
        'c': 'Immediate children, including folders',
        'd': 'Only file children',
        'e': 'Only this item'
    }
    
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Update")
        
        self.depth = component.widget.ComboBox(
            self.view.get_widget("update_depth")
        )
        for i in self.DEPTHS.values():
            self.depth.append(i)
        self.depth.set_active(0)

    def on_update_destroy(self, widget):
        gtk.main_quit()

    def on_update_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_update_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_update_revision_number_focused(self, widget, data=None):
        self.view.get_widget("update_revision_number_opt").set_active(True)

    def on_update_show_log_clicked(self, widget, data=None):
        self.logview = LogForUpdate()

class LogForUpdate(log.Log):
    def __init__(self):
        log.Log.__init__(self)
        
    def on_log_destroy(self, widget):
        self.view.hide()
    
    def on_log_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_log_ok_clicked(self, widget, data=None):
        self.view.hide()


if __name__ == "__main__":
    window = UpdateToRevision()
    gtk.main()
