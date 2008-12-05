#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.view
import component.helper

import notification

class Relocate:
    """
    Interface to relocate your working copy's repository
    
    """

    def __init__(self):
        self.view = component.view.InterfaceView(self, "relocate", "Relocate")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("to_urls"), 
            component.helper.GetRepositoryPaths()
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

if __name__ == "__main__":
    window = Relocate()
    gtk.main()
