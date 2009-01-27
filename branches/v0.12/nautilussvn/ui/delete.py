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

from nautilussvn.ui import InterfaceNonView
from nautilussvn.ui.callback import VCSAction
import nautilussvn.lib.vcs

class Delete(InterfaceNonView):
    """
    This class provides a handler to Delete functionality.
    
    """

    def __init__(self, paths):
        InterfaceNonView.__init__(self)
        self.paths = paths
        self.vcs = nautilussvn.lib.vcs.create_vcs_instance()

    def start(self):
        versioned = []
        unversioned = []
        for path in self.paths:
            if self.vcs.is_versioned(path):
                versioned.append(path)
            else:
                unversioned.append(path)
        
        result = True
        if not versioned:
            confirm = nautilussvn.ui.dialog.Confirmation(
                "One or more of the specified files is unversioned.  Do you want to send it/them to the Trash?"
            )
            result = confirm.run()
        
        if result:
            try:
                self.vcs.remove(versioned, force=True)
            except Exception, e:
                print str(e)
                
        else:
            for path in unversioned:
                nautilussvn.lib.helper.delete_item(path)
        
if __name__ == "__main__":
    from os import getcwd
    from sys import argv
    
    args = argv[1:]
    if len(args) < 1:
        raise SystemExit("Usage: python %s [path1] [path2] ..." % __file__)

    # Convert "." to current working directory
    paths = args
    i = 0
    for arg in args:
        paths[i] = arg
        if paths[i] == ".":
            paths[i] = getcwd()
        i += 1

    window = Delete(paths)
    window.register_gtk_quit()
    window.start()
