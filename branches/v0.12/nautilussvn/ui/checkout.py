#!/usr/bin/env python

import sys

import pygtk
import gobject
import gtk
import gtk.glade

import widgets
import helper
import dialogs

class Checkout:
    def __init__(self):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Checkout")
        self.wTree.signal_autoconnect(self)

        self.repositories = widgets.ComboBox(self.wTree.get_widget("co_repositories"), helper.GetRepositoryPaths())                

    def on_co_destroy(self, widget):
        gtk.main_quit()

    def on_co_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_co_ok_clicked(self, widget):
        print "OK"

    def on_co_revision_number_focused(self, widget, data=None):
        self.wTree.get_widget("co_revision_number_opt").set_active(True)

    def on_co_file_chooser_clicked(self, widget, data=None):
        chooser = dialogs.FileChooser()
        path = chooser.run()
        if path is not None:
            self.wTree.get_widget("co_destination").set_text(path)


if __name__ == "__main__":
    window = Checkout()
    gtk.main()
