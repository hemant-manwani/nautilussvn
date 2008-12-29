#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2008 by Adam Plumb <adamplumb@gmail.com>
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

from nautilussvn.ui import InterfaceView
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.lib.vcs

class Properties:
    """
    Provides an interface to add/edit/delete properties on versioned
    items in the working copy.
    
    """

    SELECTED_ROW = None

    def __init__(self, path):
        self.view = nautilussvn.ui.InterfaceView(self, "properties", "Properties")
        
        self.path = path
        self.delete_stack = []
        
        self.view.get_widget("Properties").set_title(
            "Properties - %s" % path
        )
        
        self.view.get_widget("path").set_text(path)
        
        self.table = nautilussvn.ui.widget.Table(
            self.view.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Name", "Value"]
        )
        
        self.vcs = nautilussvn.lib.vcs.VCSFactory().create_vcs_instance()
        self.proplist = self.vcs.proplist(path)
        
        for key,val in self.proplist.items():
            self.table.append([key,val])

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.save()
        gtk.main_quit()
    
    def save(self):
        for row in self.delete_stack:
            self.vcs.propdel(self.path, row[0])

        for row in self.table.get_items():
            self.vcs.propset(self.path, row[0], row[1], overwrite=True)
        
    def on_new_clicked(self, widget):
        dialog = nautilussvn.ui.dialog.Property()
        name,value = dialog.run()
        if name is not None:
            self.table.append([name,value])
    
    def on_edit_clicked(self, widget):
        (name,value) = self.get_selected_name_value()
        dialog = nautilussvn.ui.dialog.Property(name, value)
        name,value = dialog.run()
        if name is not None:
            self.set_selected_name_value(name, value)
    
    def on_delete_clicked(self, widget, data=None):
        row = self.table.get_row(self.SELECTED_ROW)
        self.delete_stack.append([row[0],row[1]])
        self.table.remove(self.SELECTED_ROW)
    
    def set_selected_name_value(self, name, value):
        self.table.set_row(self.SELECTED_ROW, [name,value])
        
    def get_selected_name_value(self):
        returner = None
        if self.SELECTED_ROW is not None:
            returner = self.table.get_row(self.SELECTED_ROW)
        return returner
    
    def on_table_button_pressed(self, treeview, event=None):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            self.SELECTED_ROW = path
            self.view.get_widget("edit").set_sensitive(True)
            self.view.get_widget("delete").set_sensitive(True)
        else:
            self.SELECTED_ROW = None
            self.view.get_widget("edit").set_sensitive(False)
            self.view.get_widget("delete").set_sensitive(False)

if __name__ == "__main__":
    window = Properties("log.py")
    gtk.main()
