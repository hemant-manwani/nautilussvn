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
    
    #
    # is
    #
    
    def is_working_copy(self, path):
        if (isdir(path) and
                isdir(os.path.join(path, ".svn"))):
            return True
        
        return False
        
    def is_in_a_or_a_working_copy(self, path):
        # If we're a file we have to check the directory we're in instead
        if isfile(path):
            path = os.path.abspath(os.path.join(path, os.path.pardir))
        
        if self.is_working_copy(path):
            return True
            
        return False
        
    def is_versioned(self, path):
        
        # info will return nothing for an unversioned file inside a working copy
        if self.client.info(path):
            return True
        
        return False
    
    def is_normal(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.normal:
            return True
        
        return False
    
    def is_added(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.added:
            return True
        
        return False
        
    def is_modified(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.modified:
            return True
        
        return False
    
    def is_deleted(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.deleted:
            return True
        
        return False
        
    #
    # has
    #
    
    def has_unversioned(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.unversioned:
                return True
                
        return False
    
    def has_added(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.added:
                return True
                
        return False
        
    def has_modified(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.modified:
                return True
        
        return False

    def has_deleted(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.deleted:
                return True
        
        return False
