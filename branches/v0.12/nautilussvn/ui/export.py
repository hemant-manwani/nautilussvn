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
from nautilussvn.ui.checkout import Checkout
from nautilussvn.ui.dialog import MessageBox
from nautilussvn.ui.callback import VCSAction
import nautilussvn.lib.helper

class Export(Checkout):
    def __init__(self, path):
        Checkout.__init__(self, path)
        self.get_widget("Checkout").set_title("Export - %s" % path)
        
        self.get_widget("url").set_text(path)
        self.get_widget("destination").set_text("")

    def on_ok_clicked(self, widget):
        url = self.get_widget("url").get_text()
        path = self.get_widget("destination").get_text()
        omit_externals = self.get_widget("omit_externals").get_active()
        recursive = self.get_widget("recursive").get_active()

        if not url or not path:
            MessageBox("You must fill in both the URL and Destination fields.")
            return
        
        if url.startswith("file://"):
            url = url[7:]
        if path.startswith("file://"):
            path = path[7:]
        
        revision = self.vcs.revision("head")
        if self.get_widget("revision_number_opt").get_active():
            revision = self.vcs.revision(
                "number",
                number=int(self.get_widget("revision_number").get_text())
            )
    
        self.hide()
        self.action = VCSAction(
            self.vcs,
            register_gtk_quit=self.gtk_quit_is_set()
        )
        
        self.action.append(self.action.set_status, "Running Export Command...")
        self.action.append(nautilussvn.lib.helper.save_repository_path, url)
        self.action.append(
            self.vcs.export,
            url,
            path,
            force=True,
            recurse=recursive,
            revision=revision,
            ignore_externals=omit_externals
        )
        self.action.append(self.action.finish)
        self.action.start()
        
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Export(args[0])
    window.register_gtk_quit()
    gtk.main()
