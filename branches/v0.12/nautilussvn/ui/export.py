#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.helper
import component.dialog
import component.view

import notification

class Export:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "export", "Export")

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()
        
if __name__ == "__main__":
    window = Export()
    gtk.main()
