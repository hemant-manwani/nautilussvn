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
from nautilussvn.ui.widget import Table

class BlameUI(InterfaceView):
    def __init__(self, blamedict):
        InterfaceView.__init__(self, "blameui", "BlameUI")

        self.table = Table(
            self.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Line", "Revision", "Author", 
                "Date", "Text"],
        )
        self.table.allow_multiple()
        for item in blamedict:
            self.table.append([
                item["number"],
                item["revision"].number,
                item["author"],
                item["date"],
                item["line"]
            ])

    def on_destroy(self, widget):
        self.close()
