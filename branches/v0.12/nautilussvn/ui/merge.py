#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.view
import component.helper

import notification

class Merge:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Merge")

    def on_merge_destroy(self, widget):
        gtk.main_quit()

    def on_merge_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_merge_forward_clicked(self, widget):
        self.view.hide()
        Merge2()

class Merge2:
    def __init__(self):
        pass

if __name__ == "__main__":
    window = Merge()
    gtk.main()
