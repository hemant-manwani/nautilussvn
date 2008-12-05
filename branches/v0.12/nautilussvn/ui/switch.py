#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.helper
import component.dialog
import component.view

import notification
import log

class Switch:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "switch", "Switch")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("repositories"), 
            component.helper.GetRepositoryPaths()
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_revision_number_focused(self, widget, data=None):
        self.view.get_widget("revision_number_opt").set_active(True)

    def on_show_log_clicked(self, widget, data=None):
        LogForSwitch(ok_clicked=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

class LogForSwitch(log.Log):
    def __init__(self, ok_clicked=None):
        log.Log.__init__(self)
        self.ok_clicked = ok_clicked
        
    def on_destroy(self, widget):
        self.view.hide()
    
    def on_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        if self.ok_clicked is not None:
            self.ok_clicked(self.get_selected_revision_number())

if __name__ == "__main__":
    window = Switch()
    gtk.main()
