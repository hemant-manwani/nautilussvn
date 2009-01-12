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

import os

import pygtk
import gobject
import gtk

from nautilussvn.ui import InterfaceView
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.callback
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

class Add(InterfaceView):
    """
    Provides an interface for the user to add unversioned files to a
    repository.  Also, provides a context menu with some extra functionality.
    
    Send a list of paths to be added
    
    """

    TOGGLE_ALL = True

    def __init__(self, paths):
        InterfaceView.__init__(self, "add", "Add")

        self.last_row_clicked = None

        self.files_table = nautilussvn.ui.widget.Table(
            self.get_widget("files_table"), 
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [nautilussvn.ui.widget.TOGGLE_BUTTON, "Path", "Extension"]
        )

        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()
        self.files = self.vcs.get_items(
            paths, 
            [self.vcs.STATUS["unversioned"]]
        )
        
        for item in self.files:
            self.files_table.append([
                True, 
                item.path, 
                nautilussvn.lib.helper.get_file_extension(item.path)
            ])
    
    def on_destroy(self, widget):
        self.close()
        
    def on_cancel_clicked(self, widget):
        self.close()

    def on_ok_clicked(self, widget):
        items = self.files_table.get_activated_rows(1)
        self.hide()

        self.action = nautilussvn.ui.callback.VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set()
        )
        
        self.action.append(self.action.set_title, "Add")
        self.action.append(self.action.set_status, "Running Add Command...")
        self.action.append(self.vcs.add, items)
        self.action.append(self.action.set_status, "Completed Add")
        self.action.append(self.action.finish)
        self.action.start()

    def on_select_all_toggled(self, widget):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.files_table.get_items():
            row[0] = self.TOGGLE_ALL

    def on_files_table_button_pressed(self, treeview, event=None, user_data=None):
        if event.button == 3:
            pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                
                treeview_model = treeview.get_model()
                fileinfo = treeview_model[path]

                self.last_row_clicked = path[0]
                
                context_menu = nautilussvn.ui.widget.ContextMenu([{
                        "label": "Open",
                        "signals": {
                            "activate": {
                                "callback": self.on_context_open_activated, 
                                "args": fileinfo
                            }
                        },
                        "condition": (lambda: True)
                    },{
                        "label": "Browse to",
                        "signals": {
                            "activate": {
                                "callback": self.on_context_browse_activated, 
                                "args": fileinfo
                            }
                        },
                        "condition": (lambda: True)
                    },{
                        "label": "Delete",
                        "signals": {
                            "activate": {
                                "callback": self.on_context_delete_activated, 
                                "args": fileinfo
                            }
                        },
                        "condition": self.condition_delete
                    },{
                        "label": "Add to ignore list",
                        'submenu': [{
                                "label": os.path.basename(fileinfo[1]),
                                "signals": {
                                    "activate": {
                                        "callback": self.on_subcontext_ignore_by_filename_activated, 
                                        "args": fileinfo
                                     }
                                 },
                                "condition": (lambda: True)
                            },
                            {
                                "label": "*%s"%fileinfo[2],
                                "signals": {
                                    "activate": {
                                        "callback": self.on_subcontext_ignore_by_fileext_activated, 
                                        "args": fileinfo
                                    }
                                },
                                "condition": (lambda: True)
                            }
                        ],
                        "condition": self.condition_ignore_submenu
                    }
                ])
                context_menu.show(event)
                
    def on_context_open_activated(self, widget, data=None):
        nautilussvn.lib.helper.open_item(data[1])
        
    def on_context_browse_activated(self, widget, data=None):
        nautilussvn.lib.helper.browse_to_item(data[1])

    def on_context_delete_activated(self, widget, data=None):
        confirm = nautilussvn.ui.dialog.Confirmation(
            "Are you sure you want to send this file to the trash?"
        )
        
        if confirm.run():
            nautilussvn.lib.helper.delete_item(data[1])
            self.files_table.remove(self.last_row_clicked)
        
    def on_subcontext_ignore_by_filename_activated(self, widget, data=None):
        prop_name = self.vcs.PROPERTIES["ignore"]
        prop_value = os.path.basename(data[1])
        
        if self.vcs.propset("", prop_name, prop_value):
            self.files_table.remove(self.last_row_clicked)
        
    def on_subcontext_ignore_by_fileext_activated(self, widget, data=None):
        prop_name = self.vcs.PROPERTIES["ignore"]
        prop_value = "*%s" % data[2]
        
        if self.vcs.propset("", prop_name, prop_value):
            self.files_table.remove(self.last_row_clicked)

    #
    # Context Menu Conditions
    #
    
    def condition_delete(self):
        return True
    
    def condition_ignore_submenu(self):
        return True
        
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) < 1:
        raise SystemExit("Usage: python %s [path1] [path2] ..." % __file__)
    window = Add(args)
    window.register_gtk_quit()
    gtk.main()
