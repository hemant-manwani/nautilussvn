"""

Our module for everything related to the Nautilus extension.
  
"""

import os
from os.path import isdir, isfile, realpath, basename

import nautilus
import gnomevfs

import anyvc
from anyvc.workdir import get_workdir_manager_for_path

from nautilussvn.util.decorators import timeit

class NautilusSvn(nautilus.InfoProvider):
    
    #: Maps statuses to emblems.
    #: TODO: should probably be possible to create this dynamically
    EMBLEMS = {
        "added" :       "nautilussvn-added",
        "deleted":      "nautilussvn-deleted",
        "removed":      "nautilussvn-deleted",
        "modified":     "nautilussvn-modified",
        "conflicted":   "nautilussvn-conflicted",
        "missing":      "nautilussvn-conflicted",
        "normal":       "nautilussvn-normal",
        "clean":        "nautilussvn-normal",
        "ignored":      "nautilussvn-ignored",
        "locked":       "nautilussvn-locked",
        "read_only":    "nautilussvn-read_only",
        "obstructed":   "nautilussvn-obstructed"
    }
    
    #: A list of statuses which count as modified (for a directory) in 
    #: TortoiseSVN emblem speak.
    MODIFIED_STATUSES = [
        "added",
        "deleted",
        "replaced",
        "modified",
        "missing"
    ]
    
    def __init__(self):
        print "Initializing nautilussvn extension"
    
    @timeit
    def update_file_info(self, item):
        """
        
        C{update_file_info} is called only when:
        
          - When you enter a directory (once for each item but only when the
            item was modified since the last time it was listed)
          - When you refresh (once for each item visible)
          - When an item viewable from the current window is created or modified
          
        This is insufficient for our purpose because:
        
          - You're not notified about items you don't see (which is needed to 
            keep the emblem for the directories above the item up-to-date)
        
        @type   item: NautilusVFSFile
        @param  item: 
        
        """
        
        if not self.valid_uri(item.get_uri()): return
        path = realpath(gnomevfs.get_local_path_from_uri(item.get_uri()))
        
        workdir_manager = get_workdir_manager_for_path(path)
        if workdir_manager:
            status = self.get_text_status(workdir_manager, path)
            if status in self.EMBLEMS:
                item.add_emblem(self.EMBLEMS[status])
            
    def get_text_status(self, workdir_manager, path):
        """
        This is a helper function for update_file_info to figure out
        the textual representation for a set of statuses.
        """
        
        statuses = [status.state for status in workdir_manager.status(paths=(path,))]
        
        # If no statuses are returned but we do have a workdir_manager
        # it means that an error occured, most likely a working copy
        # administration area (.svn directory) went missing
        if not statuses: 
            # FIXME: figure out a way to make only the directory that
            # is missing display conflicted and the rest unkown.
            return "conflicted"

        # We need to take special care of directories
        if isdir(path):
            # These statuses take precedence.
            if "conflicted" in statuses: return "conflicted"
            if "obstructed" in statuses: return "obstructed"
            
            # The following statuses take precedence over the status
            # of children.
            if statuses[0] in ["added", "modified", "deleted"]:
                return statuses[0]
            
            # A directory should have a modified status when any of its children
            # have a certain status (see modified_statuses above). Jason thought up 
            # of a nifty way to do this by using sets and the bitwise AND operator (&).
            if len(set(self.MODIFIED_STATUSES) & set(statuses[1:])):
                return "modified"
        
        # If we're not a directory we end up here.
        return statuses[0]
            
    def valid_uri(self, uri):
        """
        Check whether or not it's a good idea to have NautilusSvn do
        its magic for this URI. Some examples of URI schemes:
        
        x-nautilus-desktop:/// # e.g. mounted devices on the desktop
        
        """
        
        # TODO: integrate this into the settings manager and allow people
        # to add custom rules etc.
        
        if not uri.startswith("file://"): return False
        
        return True
