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
        pass
        
    def is_versioned(self, path):
        pass
    
    def is_unversioned(self, path):
        pass
        
    def is_added(self, path):
        pass
        
    def is_modified(self, path):
        pass
        
    #
    # has
    #
    
    def has_unversioned(self, path):
        pass
    
    def has_added(self, path):
        pass
        
    def has_modified(self, path):
        pass
