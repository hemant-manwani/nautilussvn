#!/usr/bin/env python

import pygtk
import gobject
import gtk

import dialog
import view
import widget

class Copy:
    def __init__(self):
        self.view = view.InterfaceView(self, "Copy")
        self.message = widget.TextView(self.view.get_widget("copy_message"))

    def on_copy_destroy(self, widget):
        gtk.main_quit()

    def on_copy_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_copy_ok_clicked(self, widget):
        print "OK"

    def on_copy_from_rev_focused(self, widget, data=None):
        self.view.get_widget("copy_from_rev_opt").set_active(True)

    def on_copy_previous_messages_clicked(self, widget, data=None):
        dialog = dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)

if __name__ == "__main__":
    window = Copy()
    gtk.main()
