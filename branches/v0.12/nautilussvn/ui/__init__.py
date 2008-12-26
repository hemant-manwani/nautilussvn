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

import os

import pygtk
import gobject
import gtk
import gtk.glade

class InterfaceView:
    def __init__(self, callback_obj, filename, id):
        
        path = "%s/glade/%s.glade" % (
            os.path.dirname(os.path.realpath(__file__)), 
            filename
        )
        self.tree = gtk.glade.XML(path, id)
        self.tree.signal_autoconnect(callback_obj)
        self.id = id
        
    def get_widget(self, id):
        return self.tree.get_widget(id)
        
    def hide(self):
        self.get_widget(self.id).set_property('visible', False)
        
    def show(self):
        self.get_widget(self.id).set_property('visible', True)
