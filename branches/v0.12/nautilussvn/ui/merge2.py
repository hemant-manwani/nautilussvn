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

class Merge(InterfaceView):
    def __init__(self, path):
        InterfaceView.__init__(self, "merge2", "Merge")
        self.assistant = self.get_widget("Merge")
        
        self.assistant.set_page_complete(self.assistant.get_nth_page(0), True)
        self.assistant.set_forward_page_func(self.on_forward_clicked)

    def on_destroy(self, widget):
        self.close()
    
    def on_cancel_clicked(self, widget):
        self.close()
    
    def on_close_clicked(self, widget):
        self.close()

    def on_forward_clicked(self, widget):
        current = self.assistant.get_current_page()
        next = current + 1
        if current == 0:
            if self.get_widget("mergetype_range_opt").get_active():
                next = 1
            elif self.get_widget("mergetype_reintegrate_opt").get_active():
                next = 2
            elif self.get_widget("mergetype_tree_opt").get_active():
                next = 3

        self.assistant.set_current_page(4)
        
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Merge(args[0])
    window.register_gtk_quit()
    gtk.main()
