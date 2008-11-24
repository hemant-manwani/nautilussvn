#!/usr/bin/env python

import sys

import pygtk
import gobject
import gtk
import gtk.glade

import widgets
import dialogs

class Properties:

    SELECTED_ROW = None

    def __init__(self):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Properties")
        self.wTree.signal_autoconnect(self)
        
        self.table = widgets.Table(
            self.wTree.get_widget("props_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Name", "Value"]
        )        
        self.entries = [
            ["svn:ignore", "*"],
            ["svn:externals", "*"]
        ]
        for entry in self.entries:
            self.table.append(entry)

    def on_props_destroy(self, widget):
        gtk.main_quit()

    def on_props_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_props_ok_clicked(self, widget):
        print "OK"
        
    def on_props_new_clicked(self, widget):
        dialog = dialogs.Property()
        name,value = dialog.run()
        if name is not None:
            self.entries.append([name,value])
    
    def on_props_edit_clicked(self, widget):
        (name,value) = self.get_selected_name_value()
        dialog = dialogs.Property(name, value)
        name,value = dialog.run()
        if name is not None:
            self.set_selected_name_value(name, value)
    
    def on_props_delete_clicked(self, widget, data=None):
        self.table.remove(self.SELECTED_ROW)
    
    def set_selected_name_value(self, name, value):
        self.table.set_row(self.SELECTED_ROW, [name,value])
        
    def get_selected_name_value(self):
        returner = None
        if self.SELECTED_ROW is not None:
            returner = self.table.get_row(self.SELECTED_ROW)
        return returner
    
    def on_props_table_button_pressed(self, treeview, event=None):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            self.SELECTED_ROW = path
            self.wTree.get_widget("props_edit").set_sensitive(True)
            self.wTree.get_widget("props_delete").set_sensitive(True)
        else:
            self.SELECTED_ROW = None
            self.wTree.get_widget("props_edit").set_sensitive(False)
            self.wTree.get_widget("props_delete").set_sensitive(False)

if __name__ == "__main__":
    window = Properties()
    gtk.main()
