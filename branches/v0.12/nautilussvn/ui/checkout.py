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
import nautilussvn.ui.widget
import nautilussvn.ui.notification
import nautilussvn.ui.log
import nautilussvn.ui.dialog

import nautilussvn.lib.helper

class Checkout:

    DEPTHS = [
        'Fully recursive',
        'Immediate children, including folders',
        'Only file children',
        'Only this item'
    ]

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "checkout", "Checkout")

        self.repositories = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("repositories"), 
            nautilussvn.lib.helper.get_repository_paths()
        )
        self.depth = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("depth")
        )
        for i in self.DEPTHS:
            self.depth.append(i)
        self.depth.set_active(0)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_revision_number_focused(self, widget, data=None):
        self.view.get_widget("revision_number_opt").set_active(True)

    def on_file_chooser_clicked(self, widget, data=None):
        chooser = nautilussvn.ui.dialog.FolderChooser()
        path = chooser.run()
        if path is not None:
            self.view.get_widget("destination").set_text(path)

    def on_show_log_clicked(self, widget, data=None):
        LogForCheckout(ok_clicked=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

class LogForCheckout(nautilussvn.ui.log.Log):
    def __init__(self, ok_clicked=None):
        nautilussvn.ui.log.Log.__init__(self)
        self.ok_clicked = ok_clicked
        
    def on_destroy(self, widget):
        pass
    
    def on_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        if self.ok_clicked is not None:
            self.ok_clicked(self.get_selected_revision_number())

if __name__ == "__main__":
    window = Checkout()
    gtk.main()
