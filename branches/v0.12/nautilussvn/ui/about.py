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

import nautilussvn.ui

class About:
    """
    This class provides an interface to the About window.
    Displays:
        Authors/Credits
        Version Information
        Links
    
    """

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "about", "About")

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_close_clicked(self, widget):
        gtk.main_quit()
        
if __name__ == "__main__":
    window = About()
    gtk.main()
