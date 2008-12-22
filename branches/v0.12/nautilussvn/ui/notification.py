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

class Notification:
    
    OK_ENABLED = False

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "notification", "Notification")
    
        self.table = nautilussvn.ui.widget.Table(
            self.view.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path"]
        )
            
    def on_destroy(self, widget):
        gtk.main_quit()
    
    def on_cancel_clicked(self, widget):
        gtk.main_quit()
        
    def on_ok_clicked(self, widget):
        gtk.main_quit()

    def toggle_ok_button(self):
        self.OK_ENABLED = not self.OK_ENABLED
        self.view.get_widget("ok").set_sensitive(self.OK_ENABLED)
            
    def append(self, entry):
        self.table.append(entry)

if __name__ == "__main__":
    window = Notification()
    gtk.main()
