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

import os.path
from os.path import isdir, isfile

import pysvn

class SVN:
    
    def __init__(self):
        self.client = pysvn.Client()
    
    def is_working_copy(self, file):
        if isfile(file):
            file = os.path.dirname(file)
        
        if isdir(file):
            if isdir(os.path.join(file, ".svn")):
                return True
            
        return False

    def is_versioned(self, file):
        if not self.is_working_copy(file): return False
            
        if self.client.info(file):
            return True
        return False

    def is_added(self, file):
        return self.has_status(file, pysvn.wc_status_kind.added)

    def is_modified(self, file):
        return self.has_status(file, pysvn.wc_status_kind.modified)
        
    #
    # Helper methods
    #
    
    def has_status(self, file, status):
        if not self.is_working_copy(file): return False
            
        file_statuses = self.client.status(file)
        if isfile(file):
            file_status = file_statuses[0]
            if file_status.text_status == status:
                return True
                
        if isdir(file):
            for file_status in file_statuses:
                if file_status.text_status == status:
                    return True
            
        return False
