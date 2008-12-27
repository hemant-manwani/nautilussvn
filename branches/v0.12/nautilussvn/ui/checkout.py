#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdk@gmail.com>
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

import sys

import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.callback
import nautilussvn.ui.dialog
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

class Checkout:

    def __init__(self, path):
        self.view = nautilussvn.ui.InterfaceView(self, "checkout", "Checkout")
        
        self.path = path
        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()

        self.repositories = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("repositories"), 
            nautilussvn.lib.helper.get_repository_paths()
        )
        
        self.view.get_widget("destination").set_text(path)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        
        url = self.view.get_widget("url").get_text()
        path = self.view.get_widget("destination").get_text()
        omit_externals = self.view.get_widget("omit_externals").get_active()
        recursive = self.view.get_widget("recursive").get_active()
        
        revision = self.vcs.revision("head")
        if self.view.get_widget("revision_number_opt").get_active():
            revision = self.vcs.revision(
                "number",
                int(self.view.get_widget("revision_number").get_text())
            )
    
        self.view.hide()
        self.action = nautilussvn.ui.callback.VCSAction(self.vcs)
        self.action.set_action(
            self.vcs.checkout, 
            url, 
            path, 
            recurse=recursive,
            revision=revision,
            ignore_externals=omit_externals
        )        
        self.action.set_before("Running Checkout Command...")
        self.action.start()

    def on_revision_number_focused(self, widget, data=None):
        self.view.get_widget("revision_number_opt").set_active(True)

    def on_file_chooser_clicked(self, widget, data=None):
        chooser = nautilussvn.ui.dialog.FolderChooser()
        path = chooser.run()
        if path is not None:
            self.view.get_widget("destination").set_text(path)

    def on_show_log_clicked(self, widget, data=None):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

if __name__ == "__main__":
    args = sys.argv
    args.pop(0)
    if len(args) > 0:
        window = Checkout(args[0])
        gtk.main()
    else:
        print "Usage: python checkout.py [path]"
