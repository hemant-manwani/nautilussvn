#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006 Jason Field
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
# along with NautilusSvn; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import gnomevfs
import nautilus
import pysvn

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ 
    This is the main class that implements all of our awesome features.
    
    """
    
    def __init__(self):
        pass
        
    def get_columns(self):
        """
        
        
        """
        
        pass
        
    def update_file_info(self, file):
        """
        Callback from Nautilus to get the file status. This is where the magic 
        happens! This function check the current status of *file*, and updates 
        the display with the relevant emblem.
        
        @type   file: NautilusVFSFile
        @param  file: 
        
        """
        
        # If we're not a or inside a working copy we don't even have to bother.
        
        
        # If we're a directory we have to do a recursive status check to see if
        # any files below us have modifications (added, modified or deleted).
        
        
        # Verifiying one of following statuses: 
        #   added, missing, deleted
        # is common for both single files and directories.
        
        
        pass
        
    def get_file_items(self, window, files):
        """
        Menu activated with files selected.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        @type   files: list of NautilusVFSFile
        @param  files:
        
        """
        
        pass
        
    def get_background_items(self, window, file):
        """
        Menu activated on window background.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        @type   file:   NautilusVFSFile
        @param  file:
        
        """
        
        pass
        
class NautilusMainContextMenu():
    """
    
    
    """
    
    menu = [
        {
            "identifier": "NautilusSvn::",
            "label": "",
            "tooltip": "",
            "icon": "",
            "callback": None, # A function
            "condition": None, # A function
            "submenus": [
                # etc.
            ]
        },
        # etc.
    ]
    """ This is the definition for the menu. """
    
    def __init__(self):
        pass
    
    def construct_menu(self):
        """
        
        
        """
        
        pass
        
