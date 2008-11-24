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
    
        self.cb = cb
    
        self.model = gtk.ListStore(str)
        for i in items:
            self.model.append([i])

        self.cb.set_model(self.model)

        if type(self.cb) == gtk.ComboBoxEntry:
            self.cb.set_text_column(0)
        elif type(self.cb) == gtk.ComboBox:
            cell = gtk.CellRendererText()
            self.cb.pack_start(cell, True)
            self.cb.add_attribute(cell, 'text', 0)

    def append(self, item):
        self.model.append([item])
        
    def set_active_from_value(self, value):
        index = 0
        for entry in self.model:
            if entry[0] == value:
                self.cb.set_active(index)
                return
            index += 1                
        
class TextView:
    def __init__(self, widget=None, value=""):
        if widget is None:
            self.view = gtk.TextView()
        else:
            self.view = widget
        self.buffer = gtk.TextBuffer()
        self.view.set_buffer(self.buffer)
        self.buffer.set_text(value)
        
    def get_text(self):
        return self.buffer(self.buffer.get_start_iter(), self.buffer.get_end_iter())
