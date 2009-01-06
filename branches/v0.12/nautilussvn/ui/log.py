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
        
        self.revision = self.vcs.get_revision(self.path)
        
        self.rev_start = self.revision
        self.rev_end = self.rev_start - self.LIMIT
        if self.rev_end < 1:
            self.rev_end = 1
            
        self.rev_max = self.rev_start
        self.rev_min = 1
        
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
            [gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path", "Copy From Path", "Copy From Revision"]
        )

        self.message = nautilussvn.ui.widget.TextView(
            self.get_widget("message")
        )

        self.pbar = self.get_widget("pbar")
        self.loading = True
        self.load()

    #
    # UI Signal Callback Methods
    #

    def on_destroy(self, widget, data=None):
        self.close()

    def on_cancel_clicked(self, widget, data=None):
        if self.loading:
            self.action.set_cancel(True)
        self.close()
        
    def on_ok_clicked(self, widget, data=None):
        if self.loading:
            self.action.set_cancel(True)    
        self.close()

    def on_revisions_table_button_released(self, treeview, event):
        path = treeview.get_path_at_pos(int(event.x), int(event.y))
        
        self.selected_rows = []
        self.selected_row = None
        if path is not None:
            selection = treeview.get_selection()
            self.selected_rows = selection.get_selected_rows()
            self.selected_row = self.selected_rows[0][path[0]]
            item = self.revision_items[path[0][0]]

            self.paths_table.clear()
            if selection.count_selected_rows() == 1:
                self.message.set_text(item.message)
                
                if item.changed_paths is not None:
                    for subitem in item.changed_paths:
                        
                        copyfrom_rev = ""
                        if hasattr(subitem.copyfrom_revision, "number"):
                            copyfrom_rev = subitem.copyfrom_revision.number
                        
                        self.paths_table.append([
                            subitem.action,
                            subitem.path,
                            subitem.copyfrom_path,
                            copyfrom_rev
                        ])    
                
            else:
                self.message.set_text("")
    
    def on_previous_clicked(self, widget):
        self.rev_start += self.LIMIT
        self.rev_end += self.LIMIT
        if self.rev_start > self.rev_max:
            self.rev_start = self.rev_max
            self.rev_end = self.rev_start - self.LIMIT
            if self.rev_end < 1:
                self.rev_end = 1
        
        self.load()
            
    def on_next_clicked(self, widget):
        self.rev_start -= self.LIMIT
        self.rev_end -= self.LIMIT
        if self.rev_start < self.LIMIT:
            self.rev_start = self.LIMIT
            self.rev_end = 1

        self.load()
    
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

    def check_previous_sensitive(self):
        sensitive = True
        if self.rev_start >= (self.rev_max - self.LIMIT):
            sensitive = False

        self.get_widget("previous").set_sensitive(sensitive)

    def check_next_sensitive(self):
        sensitive = True
        if self.rev_end == 1:
            sensitive = False

        self.get_widget("next").set_sensitive(sensitive)
    
    def set_start_revision(self, rev):
        self.get_widget("start").set_text(str(rev))

    def set_end_revision(self, rev):
        self.get_widget("end").set_text(str(rev))

    def initialize_revision_labels(self):
        self.set_start_revision("N/A")
        self.set_end_revision("N/A")

    #
    # Log-loading callback methods
    #

    def refresh(self):
        """
        Refresh the items in the main log table that shows Revision/Author/etc.
        
        """
        
        self.pbar.set_text("Loading...")
        
        # Make sure the int passed is the order the log call was made
        self.revision_items = self.action.get_result(1)

        if self.action.cancel == True:
            self.pbar.set_text("Cancelled")
            return

        total = len(self.revision_items)
        inc = 1 / total
        fraction = 0
        
        for item in self.revision_items:
            msg = item.message.replace("\n", " ")
            if len(msg) > 80:
                msg = "%s..." % msg[0:80]
        
            self.revisions_table.append([
                item.revision.number,
                item.author,
                datetime.fromtimestamp(item.date).strftime(DATETIME_FORMAT),
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

    def load(self):
    
        self.revision_items = []
        self.revisions_table.clear()
        self.message.set_text("")
        self.paths_table.clear()
        self.set_loading(True)
    
        self.pbar.set_text("Retrieving Log Information...")

        self.action = VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set(),
            visible=False
        )        

        # Set up an interval to make the progress bar pulse
        # The timeout is removed after the log action finishes
        self.timer = gobject.timeout_add(100, self.update_pb)

        self.action.append(self.initialize_revision_labels)
        self.action.append(
            self.vcs.log, 
            self.path,
            revision_start=self.vcs.revision("number", number=self.rev_start),
            revision_end=self.vcs.revision("number", number=self.rev_end),
            discover_changed_paths=True
        )

        self.action.append(gobject.source_remove, self.timer)
        self.action.append(self.refresh)
        self.action.append(self.check_previous_sensitive)
        self.action.append(self.check_next_sensitive)
        self.action.append(self.set_start_revision, self.rev_start)
        self.action.append(self.set_end_revision, self.rev_end)
        self.action.append(self.set_loading, False)
        self.action.start()

    def set_loading(self, loading):
        self.loading = loading

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
