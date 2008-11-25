#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.helper
import component.dialog
import component.view

import notification

class Import:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Import")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("import_repositories"), 
            component.helper.GetRepositoryPaths()
        )
        
        self.message = component.widget.TextView(
            self.view.get_widget("import_message")
        )

    def on_import_destroy(self, widget):
        gtk.main_quit()

    def on_import_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_import_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_import_previous_messages_clicked(self, widget, data=None):
        dialog = component.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)


if __name__ == "__main__":
    window = Import()
    gtk.main()
