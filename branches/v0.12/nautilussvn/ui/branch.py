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

class Branch:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "branch", "Branch")
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )
        self.urls = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("to_urls"), 
            nautilussvn.lib.helper.get_repository_paths()
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_from_revision_number_focused(self, widget, data=None):
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
    window = Branch()
    gtk.main()
