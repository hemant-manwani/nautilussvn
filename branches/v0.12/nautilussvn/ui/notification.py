#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.view

class Notification:
    
    OK_ENABLED = False

    def __init__(self):
        self.view = component.view.InterfaceView(self, "notification", "Notification")
    
        self.table = component.widget.Table(
            self.view.get_widget("notification_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path"]
        )
        self.entries = [
            ['Added', '/home/adam/Development/test.html'],
            ['Commited', '/home/adam/Development/blah.txt']
        ]
        for row in self.entries:
            self.append_to_table(row)
            
    def on_notification_destroy(self, widget):
        gtk.main_quit()
    
    def on_notification_cancel_clicked(self, widget):
        gtk.main_quit()
        
    def on_notification_ok_clicked(self, widget):
        gtk.main_quit()

    def toggle_ok_button(self):
        self.OK_ENABLED = not self.OK_ENABLED
        self.view.get_widget("notification_ok").set_sensitive(self.OK_ENABLED)
            
    def append_to_table(self, entry):
        self.table.append(entry)

if __name__ == "__main__":
    window = Notification()
    gtk.main()
