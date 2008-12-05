#!/usr/bin/env python

import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.notification

import nautilussvn.lib.helper

class Import:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "import", "Import")

        self.repositories = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("repositories"), 
            nautilussvn.lib.helper.GetRepositoryPaths()
        )
        
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_previous_messages_clicked(self, widget, data=None):
        dialog = nautilussvn.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)


if __name__ == "__main__":
    window = Import()
    gtk.main()
