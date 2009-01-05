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
from datetime import datetime

import pygtk
import gobject
import gtk

from nautilussvn.ui import InterfaceView
from nautilussvn.ui.callback import VCSAction
import nautilussvn.ui.widget
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

DATETIME_FORMAT = nautilussvn.lib.helper.DATETIME_FORMAT

class Log(InterfaceView):
    """
    Provides an interface to the Log UI
    
    """

    selected_rows = []
    selected_row = []
    
    LIMIT = 100

    def __init__(self, path):
        """
        @type   path: string
        @param  path: A path for which to get log items
        
        """
        
        InterfaceView.__init__(self, "log", "Log")
        
        self.path = path
        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()
        
        self.rev_start = self.vcs.revision("head")

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

        self.message = nautilussvn.ui.widget.TextView(
            self.get_widget("message")
        )

        self.pbar = self.get_widget("pbar")
        self.pbar.set_text("Retrieving Log Information...")
        
        # Set up an interval to make the progress bar pulse
        # The timeout is removed after the log action finishes
        self.timer = gobject.timeout_add(100, self.update_pb)
        
        self.action = VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set(),
            visible=False
        )
        
        self.action.append(
            self.vcs.log, 
            self.path,
            revision_start=self.rev_start,
            limit=self.LIMIT
        )
        self.action.append(gobject.source_remove, self.timer)
        self.action.append(self.refresh)
        self.action.start()

    #
    # UI Signal Callback Methods
    #

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
    
    #
    # Helper methods
    #
          
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

    #
    # Log-loading callback methods
    #

    def refresh(self):
        """
        Refresh the items in the main log table that shows Revision/Author/etc.
        
        """
        
        self.pbar.set_text("Loading...")
        items = self.action.get_result(0)

        total = len(items)
        inc = 1 / total
        fraction = 0
        
        for item in items:
            msg = item["message"]
            if len(msg) > 80:
                msg = "%s..." % msg[0:80]
        
            self.revisions_table.append([
                item["revision"].number,
                item["author"],
                datetime.fromtimestamp(item["date"]).strftime(DATETIME_FORMAT),
                msg
            ])
            fraction += inc
            self.update_pb(fraction)
        
        self.pbar.set_text("Finished")
        
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
