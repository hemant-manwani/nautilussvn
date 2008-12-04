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
            self.view.get_widget("switch_repositories"), 
            component.helper.GetRepositoryPaths()
        )

    def on_switch_destroy(self, widget):
        gtk.main_quit()

    def on_switch_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_switch_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_switch_revision_number_focused(self, widget, data=None):
        self.view.get_widget("switch_revision_number_opt").set_active(True)

    def on_switch_show_log_clicked(self, widget, data=None):
        self.logview = LogForSwitch()

class LogForSwitch(log.Log):
    def __init__(self):
        log.Log.__init__(self)
        
    def on_log_destroy(self, widget):
        self.view.hide()
    
    def on_log_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_log_ok_clicked(self, widget, data=None):
        self.view.hide()

if __name__ == "__main__":
    window = Switch()
    gtk.main()
