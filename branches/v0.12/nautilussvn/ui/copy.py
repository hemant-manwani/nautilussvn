#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.dialog
import component.view
import component.widget

import notification

class Copy:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Copy")
        self.message = component.widget.TextView(
            self.view.get_widget("copy_message")
        )

    def on_copy_destroy(self, widget):
        gtk.main_quit()

    def on_copy_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_copy_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_copy_from_rev_focused(self, widget, data=None):
        self.view.get_widget("copy_from_rev_opt").set_active(True)

    def on_copy_previous_messages_clicked(self, widget, data=None):
        dialog = component.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)

if __name__ == "__main__":
    window = Copy()
    gtk.main()
