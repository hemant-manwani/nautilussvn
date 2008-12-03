#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.view
import component.helper

import log
import notification

class MergeType:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "MergeType")

    def on_mergetype_destroy(self, widget):
        gtk.main_quit()

    def on_mergetype_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergetype_forward_clicked(self, widget):
        self.view.hide()
        MergeRange()

class MergeRange:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "MergeRange")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("mergerange_from_urls"), 
            component.helper.GetRepositoryPaths()
        )

    def on_mergerange_destroy(self, widget):
        gtk.main_quit()

    def on_mergerange_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergerange_back_clicked(self, widget):
        self.view.hide()

    def on_mergerange_forward_clicked(self, widget):
        self.view.hide()
        
    def on_mergerange_show_log1_clicked(self, widget):
        LogForMerge()
        
    def on_mergerange_show_log2_clicked(self, widget):
        LogForMerge()

class LogForMerge(log.Log):
    def __init__(self):
        log.Log.__init__(self)
        
    def on_log_destroy(self, widget):
        self.view.hide()
    
    def on_log_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_log_ok_clicked(self, widget, data=None):
        self.view.hide()

if __name__ == "__main__":
    window = MergeType()
    gtk.main()
