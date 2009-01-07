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
from nautilussvn.ui.add import Add
from nautilussvn.ui.callback import VCSAction
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.callback
import nautilussvn.lib.helper

class Resolve(Add):
    def __init__(self, paths):
        InterfaceView.__init__(self, "add", "Add")

        self.window = self.get_widget("Add")
        self.window.set_title("Resolve")

        self.last_row_clicked = None

        self.files_table = nautilussvn.ui.widget.Table(
            self.get_widget("files_table"), 
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [nautilussvn.ui.widget.TOGGLE_BUTTON, "Path", "Extension"]
        )

        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()
        self.files = self.vcs.get_items(
            paths, 
            [self.vcs.STATUS["conflicted"]]
        )
        
        for item in self.files:
            self.files_table.append([
                True, 
                item.path, 
                nautilussvn.lib.helper.get_file_extension(item.path)
            ])
                    
    def on_ok_clicked(self, widget):
        items = self.files_table.get_activated_rows(1)
        self.hide()

        self.action = nautilussvn.ui.callback.VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set()
        )
        
        self.action.append(self.action.set_status, "Running Resolve Command...")
        for item in items:
            self.action.append(self.vcs.resolve, item, recurse=True)
        self.action.append(self.action.set_status, "Completed Resolve")
        self.action.append(self.action.finish)
        self.action.start()

    #
    # Context Menu Conditions
    #
    
    def condition_delete(self):
        return False

    def condition_ignore_submenu(self):
        return False
        
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) < 1:
        raise SystemExit("Usage: python %s [path1] [path2] ..." % __file__)
    window = Resolve(args)
    window.register_gtk_quit()
    gtk.main()
