#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
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

import nautilussvn.ui
import nautilussvn.ui.dialog
import nautilussvn.ui.widget
import nautilussvn.ui.notification
import nautilussvn.lib.helper
import nautilussvn.lib.vcs

class Branch:
    def __init__(self, path):
        self.view = nautilussvn.ui.InterfaceView(self, "branch", "Branch")
        
        self.vcs = nautilussvn.lib.vcs.VCSFactory().create_vcs_instance()
        
        url = self.vcs.get_repo_url(path)
        
        self.view.get_widget("from_url").set_text(url)
        self.view.get_widget("to_url").set_text(url)
        
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )
        self.urls = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("to_urls"), 
            nautilussvn.lib.helper.get_repository_paths()
        )
        
        if self.vcs.has_modified(path):
            self.tooltips = gtk.Tooltips()
            self.tooltips.set_tip(
                self.view.get_widget("from_revision_number_opt"),
                "There have been modifications to your working copy.  If you copy from the HEAD revision you will lose your changes."
            )
            self.set_revision_number_opt_active()
            self.view.get_widget("from_revision_number").set_text(
                str(self.vcs.get_revision(path))
            )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_from_revision_number_focused(self, widget, data=None):
        self.set_revision_number_opt_active()
        
    def set_revision_number_opt_active(self):
        self.view.get_widget("from_revision_number_opt").set_active(True)

    def on_previous_messages_clicked(self, widget, data=None):
        dialog = nautilussvn.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
            
    def on_show_log_clicked(self, widget, data=None):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("from_revision_number_opt").set_active(True)
            self.view.get_widget("from_revision_number").set_text(data)

if __name__ == "__main__":
    window = Branch("/home/adam/Development/nautilussvn/branches/v0.12/nautilussvn/ui/add.py")
    gtk.main()
