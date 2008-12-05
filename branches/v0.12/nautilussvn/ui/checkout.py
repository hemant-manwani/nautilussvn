#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.helper
import component.dialog
import component.view

import log
import notification

class Checkout:

    DEPTHS = [
        'Fully recursive',
        'Immediate children, including folders',
        'Only file children',
        'Only this item'
    ]

    def __init__(self):
        self.view = component.view.InterfaceView(self, "checkout", "Checkout")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("repositories"), 
            component.helper.GetRepositoryPaths()
        )
        self.depth = component.widget.ComboBox(
            self.view.get_widget("depth")
        )
        for i in self.DEPTHS:
            self.depth.append(i)
        self.depth.set_active(0)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = notification.Notification()

    def on_revision_number_focused(self, widget, data=None):
        self.view.get_widget("revision_number_opt").set_active(True)

    def on_file_chooser_clicked(self, widget, data=None):
        chooser = component.dialog.FileChooser()
        path = chooser.run()
        if path is not None:
            self.view.get_widget("destination").set_text(path)

    def on_show_log_clicked(self, widget, data=None):
        LogForCheckout(ok_clicked=self.on_closed)
    
    def on_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

class LogForCheckout(log.Log):
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
    window = Checkout()
    gtk.main()
