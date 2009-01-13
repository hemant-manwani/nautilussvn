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
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.callback
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
        
        self.get_widget("path").set_text(self.path)

    def on_destroy(self, widget):
        self.close()

    def on_cancel_clicked(self, widget):
        self.close()

    def on_ok_clicked(self, widget):
        self.close()
    
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

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Blame(args[0])
    window.register_gtk_quit()
    gtk.main()
