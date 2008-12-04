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
    """
    Provides an interface for the Merge Wizard Step 2a (Range of Revisions)
    """
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
        LogForMerge(ok_callback=self.on_log1_closed, multiple=True)
    
    def on_log1_closed(self, data):
        self.view.get_widget("mergerange_revisions").set_text(data)
    
    def on_mergerange_show_log2_clicked(self, widget):
        LogForMerge()
        
class MergeBranch:
    """
    Provides an interface for the Merge Wizard Step 2b (Reintegrate Branch)
    """
    def __init__(self):
        self.view = component.view.InterfaceView(self, "MergeBranch")

        self.repositories = component.widget.ComboBox(
            self.view.get_widget("mergebranch_from_urls"), 
            component.helper.GetRepositoryPaths()
        )

    def on_mergebranch_destroy(self, widget):
        gtk.main_quit()

    def on_mergebranch_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergebranch_back_clicked(self, widget):
        self.view.hide()

    def on_mergebranch_forward_clicked(self, widget):
        self.view.hide()
        
    def on_mergebranch_show_log1_clicked(self, widget):
        LogForMerge()

    def on_mergebranch_show_log2_clicked(self, widget):
        LogForMerge()

class MergeTree:
    """
    Provides an interface for the Merge Wizard Step 2c (Merge two trees)
    """
    def __init__(self):
        self.view = component.view.InterfaceView(self, "MergeTree")

        previous_urls = component.helper.GetRepositoryPaths()
        self.from_urls = component.widget.ComboBox(
            self.view.get_widget("mergetree_from_urls"), 
            previous_urls
        )
        self.to_urls = component.widget.ComboBox(
            self.view.get_widget("mergetree_to_urls"), 
            previous_urls
        )

    def on_mergetree_destroy(self, widget):
        gtk.main_quit()

    def on_mergetree_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergetree_back_clicked(self, widget):
        self.view.hide()

    def on_mergetree_forward_clicked(self, widget):
        self.view.hide()
        
    def on_mergetree_from_show_log_clicked(self, widget):
        LogForMerge(ok_callback=self.on_from_log_closed, multiple=False)

    def on_from_log_closed(self, data):
        self.view.get_widget("mergetree_from_revision_number").set_text(data)
        self.view.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_show_log_clicked(self, widget):
        LogForMerge(ok_callback=self.on_to_log_closed, multiple=False)

    def on_to_log_closed(self, data):
        self.view.get_widget("mergetree_to_revision_number").set_text(data)
        self.view.get_widget("mergetree_to_revision_number_opt").set_active(True)

    def on_mergetree_working_copy_show_log_clicked(self, widget):
        LogForMerge()
        
    def on_mergetree_from_revision_number_focused(self, widget, data):
        self.view.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_revision_number_focused(self, widget, data):
        self.view.get_widget("mergetree_to_revision_number_opt").set_active(True)

class LogForMerge(log.Log):
    def __init__(self, ok_callback=None, multiple=False):
        """
        Override the normal Log class so that we can hide the window as we need.
        Also, provide a callback for when the OK button is clicked so that we
        can get some desired data.
        """
        log.Log.__init__(self)
        self.ok_callback = ok_callback
        self.multiple = multiple
        
    def on_log_destroy(self, widget):
        self.view.hide()
    
    def on_log_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_log_ok_clicked(self, widget, data=None):
        self.view.hide()
        if self.ok_callback is not None:
            if self.multiple == True:
                self.ok_callback(self.get_selected_revision_numbers())
            else:
                self.ok_callback(self.get_selected_revision_number())
        

if __name__ == "__main__":
    window = MergeTree()
    gtk.main()
