#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.helper
import component.dialog
import component.view

import notification

class Checkout:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Checkout")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("co_repositories"), 
            component.helper.GetRepositoryPaths()
        )                

    def on_co_destroy(self, widget):
        gtk.main_quit()

    def on_co_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_co_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_co_revision_number_focused(self, widget, data=None):
        self.view.get_widget("co_revision_number_opt").set_active(True)

    def on_co_file_chooser_clicked(self, widget, data=None):
        chooser = component.dialog.FileChooser()
        path = chooser.run()
        if path is not None:
            self.view.get_widget("co_destination").set_text(path)


if __name__ == "__main__":
    window = Checkout()
    gtk.main()
