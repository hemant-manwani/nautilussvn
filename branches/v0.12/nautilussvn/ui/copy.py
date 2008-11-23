#!/usr/bin/env python

import sys

import pygtk
import gobject
import gtk
import gtk.glade

import dialogs

class Copy:
    def __init__(self):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Copy")
        self.wTree.signal_autoconnect(self)

        ### Get Message Box and create a text buffer for it ###
        self.message = self.wTree.get_widget("copy_message")
        self.buffer = gtk.TextBuffer()
        self.message.set_buffer(self.buffer)

    def on_copy_destroy(self, widget):
        gtk.main_quit()

    def on_copy_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_copy_ok_clicked(self, widget):
        print "OK"

    def on_copy_from_rev_focused(self, widget, data=None):
        self.wTree.get_widget("copy_from_rev_opt").set_active(True)

    def on_copy_previous_messages_clicked(self, widget, data=None):
        dialog = dialogs.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.buffer.set_text(message)

if __name__ == "__main__":
    window = Copy()
    gtk.main()
