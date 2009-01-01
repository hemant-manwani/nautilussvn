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
import nautilussvn.ui.notification

class Lock:

    TOGGLE_ALL = False

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "lock", "Lock")

        self.files_table = nautilussvn.ui.widget.Table(
            self.view.get_widget("files_table"),
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [nautilussvn.ui.widget.TOGGLE_BUTTON, "Path", "Extension", 
                "Lock", "Needs lock"],
        )
        
        self.files = [
            [True, "init/test.php", ".php", "", ""],
            [False, "added.php", ".php", "", ""]
        ]
        self.files_table.clear()
        for row in self.files:
            self.files_table.append(row)
        
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )
    
    def on_destroy(self, widget):
        gtk.main_quit()
        
    def on_cancel_clicked(self, widget, data=None):
        gtk.main_quit()
        
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()
    
    def on_select_all_toggled(self, widget, data=None):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.files_table.get_items():
            row[0] = self.TOGGLE_ALL

    def on_files_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            treeview_model = treeview.get_model()
            fileinfo = treeview_model[path]
            
            if event.button == 3:
                context_menu = nautilussvn.ui.widget.ContextMenu([{
                        'label': 'Compare with base',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_diff_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Show log',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_show_log_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Open',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_open_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Browse',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_browse_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Delete',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_delete_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Properties',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_properties_activated, 
                                'args':fileinfo
                            }
                        }
                    }
                ])
                context_menu.show(event)

    def on_files_table_row_doubleclicked(self, treeview, event, col):
        treeview.grab_focus()
        treeview.set_cursor(event[0], col, 0)
        treeview_model = treeview.get_model()
        fileinfo = treeview_model[event[0]]
        
        print "Row Double-clicked"

    def on_context_show_log_activated(self, widget, data=None):
        print "Show log Item"

    def on_context_diff_activated(self, widget, Data=None):
        print "Diff Item"

    def on_context_open_activated(self, widget, data=None):
        print "Open Item"
        
    def on_context_browse_activated(self, widget, data=None):
        print "Browse Item"

    def on_context_delete_activated(self, widget, data=None):
        print "Delete Item"
        
    def on_context_properties_activated(self, widget, data=None):
        print "Properties Item"
        
    def on_previous_messages_clicked(self, widget, data=None):
        dialog = nautilussvn.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
        
if __name__ == "__main__":
    window = Lock()
    gtk.main()
