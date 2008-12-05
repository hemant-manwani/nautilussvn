#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.dialog
import component.view
import component.widget

import notification
import log

class Copy:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "copy", "Copy")
        self.message = component.widget.TextView(
            self.view.get_widget("message")
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_from_revision_number_focused(self, widget, data=None):
        self.view.get_widget("from_revision_number_opt").set_active(True)

    def on_previous_messages_clicked(self, widget, data=None):
        dialog = component.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
            
    def on_show_log_clicked(self, widget, data=None):
        LogForCopy(ok_clicked=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("from_revision_number_opt").set_active(True)
            self.view.get_widget("from_revision_number").set_text(data)

class LogForCopy(log.Log):
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
    window = Copy()
    gtk.main()
