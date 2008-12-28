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

import pygtk
import gobject
import gtk

from nautilussvn.ui import InterfaceView
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.notification

class Update:
    """
    This class provides an interface to generate an "update".
    Pass it a path and it will start an update, running the notification dialog.  
    There is no glade view.
    
    """

    def __init__(self):
        self.notification = nautilussvn.ui.notification.Notification()


class UpdateToRevision:
    """
    This class provides an interface to update a working copy to a specific
    revision.  It has a glade view.
    
    """
    
    DEPTHS = {
        'a': 'Working Copy',
        'b': 'Fully recursive',
        'c': 'Immediate children, including folders',
        'd': 'Only file children',
        'e': 'Only this item'
    }
    
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "update", "Update")
        
        self.depth = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("depth")
        )
        for i in self.DEPTHS.values():
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

    def on_show_log_clicked(self, widget, data=None):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

if __name__ == "__main__":
    window = UpdateToRevision()
    gtk.main()
