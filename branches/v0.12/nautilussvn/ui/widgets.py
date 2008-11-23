#!/usr/bin/env python

import sys
import pygtk
import gtk
import gobject
import gtk.glade
    
TOGGLE_BUTTON = 'TOGGLE_BUTTON'

class Table:
    def __init__(self, treeview, coltypes, colnames, values=[]):
        self.liststore = gtk.ListStore(*coltypes)
        for row in values:
            self.liststore.append(row)

        self.treeview = treeview
        self.treeview.set_model(self.liststore)

        self.cols = []
        self.cells = {}
        i = 0
        for name in colnames:
            if name == TOGGLE_BUTTON:
                cell = gtk.CellRendererToggle()
                cell.set_property('activatable', True)
                cell.connect("toggled", self.toggled_cb, i)
                col = gtk.TreeViewColumn("", cell)
                col.set_attributes(cell, active=i)
            else:
                cell = gtk.CellRendererText()
                cell.set_property('yalign', 0)
                col = gtk.TreeViewColumn(name, cell)
                col.set_attributes(cell, text=i)

            self.treeview.append_column(col)
            i += 1

    def toggled_cb(self, cell, path, column):
        model = self.treeview.get_model()
        model[path][column] = not model[path][column]

    def append(self, row):
        self.liststore.append(row)

    def remove(self, index):
        model = self.treeview.get_model()
        del model[index]

    def get_items(self):
        return self.treeview.get_model()

    def clear(self):
        self.treeview.get_model().clear()

class ComboBox:
    def __init__(self, cb, items):
        self.model = gtk.ListStore(str)
        for i in items:
            self.model.append([i])

        cb.set_model(self.model)

        if type(cb) == gtk.ComboBoxEntry:
            cb.set_text_column(0)
        elif type(cb) == gtk.ComboBox:
            cell = gtk.CellRendererText()
            cb.pack_start(cell, True)
            cb.add_attribute(cell, 'text', 0)

    def append(self, item):
        self.model.append([item])
