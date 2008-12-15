#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
# 
# NautilusSvn is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# NautilusSvn is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NautilusSvn;  If not, see <http://www.gnu.org/licenses/>.
#

import pygtk
import gobject
import gtk

import nautilussvn.lib.helper
    
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
        
    def get_row(self, index):
        model = self.treeview.get_model()
        return model[index]
    
    def set_row(self, index, row):
        model = self.treeview.get_model()
        model[index] = row
        
    def allow_multiple(self):
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

class ComboBox:
    def __init__(self, cb, items=None):
    
        self.cb = cb
    
        self.model = gtk.ListStore(str)
        if items is not None:
            for i in items:
                self.append(i)

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
    
    def get_active_text(self):
        return self.cb.get_active_text()     
    
    def set_active(self, index):
        self.cb.set_active(index)       
        
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
        return self.buffer.get_text(
            self.buffer.get_start_iter(), 
            self.buffer.get_end_iter()
        )
        
    def set_text(self, text):
        self.buffer.set_text(text)
        
class ContextMenu:
    def __init__(self, menu):
        if menu is None:
            return
        
        self.view = gtk.Menu()
        for item in menu:
            menuitem = gtk.MenuItem(item['label'])
            if 'signals' in item:
                for signal, info in item['signals'].items():
                    menuitem.connect(signal, info['callback'], info['args'])
            
            if 'submenu' in item:
                submenu = ContextMenu(item['submenu'])
                menuitem.set_submenu(submenu.get_widget())
            
            self.view.add(menuitem)
        
    def show(self, event):        
        self.view.show_all()
        self.view.popup(None, None, None, event.button, event.time)
        
    def get_widget(self):
        return self.view
