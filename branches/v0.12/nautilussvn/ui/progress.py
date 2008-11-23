#!/usr/bin/env python

import sys

import pygtk
import gobject
import gtk
import gtk.glade

import dialogs

class ProgressTest:
    def __init__(self):
        dialog = dialogs.Progress()
        result = dialog.run()

if __name__ == "__main__":
    window = ProgressTest()
    gtk.main()
