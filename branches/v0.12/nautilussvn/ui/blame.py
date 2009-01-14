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
from nautilussvn.ui.log import LogDialog
from nautilussvn.ui.callback import VCSAction
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

class Blame(InterfaceView):
    """
    Provides a UI interface to annotate items in the repository or
    working copy.
    
    Pass a single path to the class when initializing
    
    """
    
    def __init__(self, path):
        InterfaceView.__init__(self, "blame", "Blame")
        
        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()
        
        self.path = path
        self.pbar = nautilussvn.ui.widget.ProgressBar(self.get_widget("pbar"))
        self.is_loading = False
        self.action = None
        
    def on_destroy(self, widget):
        self.close()

    def on_cancel_clicked(self, widget):
        if self.is_loading:
            self.action.set_cancel(True)
            self.pbar.set_text("Cancelled")
            self.pbar.update(1)
            self.set_loading(False)
        else:
            self.close()

    def on_ok_clicked(self, widget):
    
        if self.action is not None:
            self.close()
            return
    
        self.set_loading(True)
        self.pbar.set_text("Retrieving Blame Information...")
        self.pbar.start_pulsate()
        
        self.action = VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set(),
            visible=False
        )        

        from_rev_num = int(self.get_widget("from_revision").get_text())
        if not from_rev_num:
            nautilussvn.ui.dialog.MessageBox("You must specify a FROM revision.")
            return
            
        from_rev = self.vcs.revision("number", number=from_rev_num)
        
        to_rev = None
        if self.get_widget("revision_head_opt").get_active():
            to_rev = self.vcs.revision("head")
        elif self.get_widget("revision_number_opt").get_active():
            rev_num = self.get_widget("revision_number").get_text()
            
            if rev_num == "":
                nautilussvn.ui.dialog.MessageBox("You must specify a TO revision.")
                return
                
            to_rev = self.vcs.revision("number", number=rev_num)

        
        self.action.append(
            self.vcs.annotate, 
            self.path,
            from_rev,
            to_rev
        )
        self.action.append(self.pbar.update, 1)
        self.action.append(self.pbar.set_text, "Completed")
        self.action.append(self.launch_blame)
        self.action.start()

    
    def on_revision_number_focused(self, widget, data=None):
        self.set_revision_number_opt_active()
        
    def set_revision_number_opt_active(self):
        self.get_widget("revision_number_opt").set_active(True)

    def on_show_log_clicked(self, widget, data=None):
        LogDialog(self.path, ok_callback=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.set_revision_number_opt_active()
            self.get_widget("revision_number").set_text(data)

    #
    # Helper methods
    #

    def launch_blame(self):
        blame = self.action.get_result(0)
        message = ""
        for item in blame:
            message = "%s%s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (
                message,
                item["number"],
                item["date"],
                item["revision"].number,
                item["author"],
                item["line"]
            )
        
        open("/tmp/blame.tmp", "w").write(message)
        nautilussvn.lib.helper.open_item("/tmp/blame.tmp")
        self.close()
    
    def set_loading(self, loading=True):
        self.is_loading = loading

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Blame(args[0])
    window.register_gtk_quit()
    gtk.main()
