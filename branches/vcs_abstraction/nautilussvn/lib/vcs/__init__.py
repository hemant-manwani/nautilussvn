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

from nautilussvn.lib import StatusMonitor
from nautilussvn.lib.vcs.svn import SVNClient, SVNStatusMonitor
from nautilussvn.lib.decorators import deprecated

@deprecated
def create_vcs_instance():
    # TODO: remove this once all classes are converted to this new style
    return SVNClient()
    
class VCSClient:
    
    def is_valid_path(self, path):
        """
        This function is used to verify whether a certain path is a working
        copy for a particular VCS.
        
        This function needs to be implemented by all subclasses.
        
        @type   path:   string
        @type   path:   The path for which to check what VCS it belongs to.
        
        @rtype:         boolean
        @return:        A boolean indicating whether path belongs to VCS.
        """
        
        return False

class VCSFactory:
    
    @deprecated
    def create_vcs_instance(self):
        """
        @deprecated: Use nautilussvn.lib.vcs.create_vcs_instance() instead.
        """
        
        return SVN()
        
class VCSStatusMonitor():
    """
    
    The C{StatusMonitor} is basically a replacement for the currently limited 
    C{update_file_info} function.
    
    What C{StatusMonitor} does:
    
      - When somebody adds a watch and if there's not already a watch for this 
        item it will add one and do an initial status check.
    
      - Use inotify to keep track of modifications of any watched items
        (we actually only care about modifications not creations and deletions)
        
      - Either on request, or when something interesting happens, it checks
        the status for an item which means:
        
          - See working code for exactly what a status check means
        
          - After checking the status for an item, if there's a watch for
            a parent directory this is what will happen:    
        
              - If status is (vcs) modified, (vcs) added or (vcs) deleted:
            
                  - For every parent the callback will be called with status 
                    "modified" (since it cannot be any other way)
          
              - If vcs status is normal: 
            
                  - A status check is done for the parent directory since we 
                    cannot be sure what the status for them is
      
    In the future we might implement a functionality which also monitors
    versioning actions so the command-line client can be used and still have
    the emblems update accordingly. 
    
    UML sequence diagram depicting how the StatusMonitor is used::

        +---------------+          +-----------------+         
        |  NautilusSVN  |          |  StatusMonitor  |         
        +---------------+          +-----------------+         
               |                            |                  
               |   new(self.cb_status)      |                  
               |--------------------------->|                  
               |                            |                  
               |     add_watch(path)        |                  
               |--------------------------->|---+              
               |                            |   |              
               |  cb_status(path, status)   |   | status(path) 
               |<---------------------------|<--+              
               |                            |                  
               |---+                        |                  
               |   | set_emblem_by_status(path, status)      
               |<--+                        |                  
               |                            |                  

    
    """
    
    def __init__(self, callback):
        self.status_monitor = StatusMonitor(self.callback)
        self.vcs_status_monitor = SVNStatusMonitor(callback, self.status_monitor)
        
    def add_watch(self, path):
        self.vcs_status_monitor.add_watch(path)
        
    def callback(self, path):
        self.vcs_status_monitor.status(path, invalidate=True)
