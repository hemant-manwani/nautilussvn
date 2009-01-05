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

from __future__ import division
import threading

import pygtk
import gobject
import gtk

from nautilussvn.ui import InterfaceView
from nautilussvn.ui.callback import VCSAction
import nautilussvn.ui.widget
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

class Log(InterfaceView):

    selected_rows = []
    selected_row = []

    def __init__(self, path):
        InterfaceView.__init__(self, "log", "Log")
        
        self.path = path
        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()

        self.revisions_table = nautilussvn.ui.widget.Table(
            self.get_widget("revisions_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Revision", "Author", 
                "Date", "Message"]
        )
        self.revisions_table.allow_multiple()

        self.paths_table = nautilussvn.ui.widget.Table(
            self.get_widget("paths_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path"]
        )
        self.paths = [
            ["Added", "test.html"],
            ["Committed", "index.html"]
        ]
        for row in self.paths:
            self.paths_table.append(row)

        self.message = nautilussvn.ui.widget.TextView(
            self.get_widget("message")
        )

        self.pbar = self.get_widget("pbar")
        self.load()

    def on_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_cancel_clicked(self, widget, data=None):
        gtk.main_quit()
        
    def on_ok_clicked(self, widget, data=None):
        self.close()

    def on_revisions_table_button_released(self, treeview, event):
        path = treeview.get_path_at_pos(int(event.x), int(event.y))
        
        self.selected_rows = []
        self.selected_row = None
        if path is not None:
            selection = treeview.get_selection()
            self.selected_rows = selection.get_selected_rows()
            self.selected_row = self.selected_rows[0][path[0]]

            if selection.count_selected_rows() == 1:
                self.message.set_text(self.selected_row[3])
            else:
                self.message.set_text("")
                
    def get_selected_revision_numbers(self):
        if len(self.selected_rows) == 0:
            return ""

        rows = []
        for row in self.selected_rows[1]:
            rows.append(int(row[0]))

        returner = []
        for row in rows:
            returner.append(int(self.selected_rows[0][row][0]))

        returner.sort()
        return nautilussvn.lib.helper.encode_revisions(returner)

    def get_selected_revision_number(self):
        if len(self.selected_row):
            return self.selected_row[0]
        else:
            return ""

    def update_revisions(self):
    
        self.pbar.set_text("Loading...")
        items = self.action.get_result(0)
    
        total = len(items)
        inc = 1 / total
        fraction = 0
        
        for item in items:
            self.revisions_table.append([
                item["revision"].number,
                item["author"],
                str(item["date"]),
                item["message"]
            ])
            fraction += inc
            self.update_pb(fraction)
        
        self.pbar.set_text("Finished")

    def load(self):
        self.pbar.set_text("Retrieving Log Information...")
        self.timer = gobject.timeout_add(100, self.update_pb)
        
        self.action = VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set(),
            visible=False
        )
        
        self.action.append(self.vcs.client.log, self.path)
        self.action.append(gobject.source_remove, self.timer)
        self.action.append(self.update_revisions)
        self.action.start()
        
    def update_pb(self, fraction=None):
        if fraction:
            if fraction > 1:
                fraction = 1
            self.pbar.set_fraction(fraction)
            return False
        else:
            self.pbar.pulse()
            return True

class LogDialog(Log):
    def __init__(self, ok_callback=None, multiple=False):
        """
        Override the normal Log class so that we can hide the window as we need.
        Also, provide a callback for when the OK button is clicked so that we
        can get some desired data.
        """
        Log.__init__(self)
        self.ok_callback = ok_callback
        self.multiple = multiple
        
    def on_destroy(self, widget):
        pass
    
    def on_cancel_clicked(self, widget, data=None):
        self.hide()
    
    def on_ok_clicked(self, widget, data=None):
        self.hide()
        if self.ok_callback is not None:
            if self.multiple == True:
                self.ok_callback(self.get_selected_revision_numbers())
            else:
                self.ok_callback(self.get_selected_revision_number())

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Log(args[0])
    window.register_gtk_quit()
    gtk.main()
