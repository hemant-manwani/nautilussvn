"""

Our module for everything related to the Nautilus extension.
  
"""

from __future__ import with_statement

from os.path import realpath

import nautilus
import gnomevfs

from nautilussvn.util.vcs import get_summarized_status

import dbus.mainloop.glib
import nautilussvn.dbus.service
from nautilussvn.dbus.statuschecker import StatusCheckerStub as StatusChecker

# Start up our DBus service if it's not already started, if this fails
# we can't really do anything.
nautilussvn.dbus.service.start()

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider):

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
        "obstructed":   "nautilussvn-obstructed",
        "unversioned":  "nautilussvn-unversioned",
        "unknown":      "nautilussvn-unknown",
        "calculating":  "nautilussvn-calculating"
    }
    
    #: This is our lookup table for C{NautilusVFSFile}s which we need for attaching
    #: emblems. This is mostly a workaround for not being able to turn a path/uri
    #: into a C{NautilusVFSFile}. It looks like:::
    #: 
    #:     nautilusVFSFile_table = {
    #:        "/foo/bar/baz": <NautilusVFSFile>
    #:     
    #:     }
    #: 
    #: Keeping track of C{NautilusVFSFile}s is a little bit complicated because
    #: when an item is moved (renamed) C{update_file_info} doesn't get called. So
    #: we also add C{NautilusVFSFile}s to this table from C{get_file_items} which
    #: gets called when an item is selected.
    nautilusVFSFile_table = {}
    
    #: Keep track of item statuses locally. Due to the way everything works
    #: if we didn't do this we'd request statuses from the daemon too often.
    #: 
    #:     statuses = {
    #:         "/foo/bar/baz": [
    #:             ("/foo/bar/baz", "normal"),
    #:             ("/foo/bar/baz/quux", "modified")
    #:         ]
    #:     }
    #: 
    statuses = {}
    
    def __init__(self):
        self.status_checker = StatusChecker(self.cb_status)
        
    def update_file_info(self, item):
        """
        C{update_file_info} is called when:
        
          - When you enter a directory (once for each item but only when the
            item was modified since the last time it was listed)
          - When you refresh (once for each item visible)
          - When an item viewable from the current window is created or modified
        
        You are not notified about items that are not visible.
        """
        
        if not self.valid_uri(item.get_uri()): return
        path = realpath(gnomevfs.get_local_path_from_uri(item.get_uri()))
        
        # Always replace the item in the table with the one we receive, because
        # for example if an item is deleted and recreated the NautilusVFSFile
        # we had before will be invalid (think pointers and such).
        self.nautilusVFSFile_table[path] = item
        
        # If we are able to set an emblem that means we have a local status
        # available. The StatusMonitor will keep us up-to-date through the 
        # C{cb_status} callback.
        if self.set_emblem_by_path(path): return
        
        # Otherwise request an initial status check to be done.
        self.status_checker.check_status(path, recurse=True)
        
    def get_file_items(self, window, items):
        """
        Menu activated with items selected. Nautilus also calls this function
        when rendering submenus, even though this is not needed since the entire
        menu has already been returned.
        
        Note that calling C{nautilusVFSFile.invalidate_extension_info()} will 
        also cause this function to be called.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   items:  list of NautilusVFSFile
        @param  items:
        
        @rtype:         list of MenuItems
        @return:        The context menu entries to add to the menu.
        
        """
        
        paths = []
        for item in items:
            if self.valid_uri(item.get_uri()):
                path = realpath(gnomevfs.get_local_path_from_uri(item.get_uri()))
                paths.append(path)
                self.nautilusVFSFile_table[path] = item

        if len(paths) == 0: return []
        
        # TODO:
        return []
        
    def get_background_items(self, window, item):
        """
        Menu activated on entering a directory. Builds context menu for File
        menu and for window background.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   item:   NautilusVFSFile
        @param  item:
        
        @rtype:         list of MenuItems
        @return:        The context menu entries to add to the menu.
        
        """
        
        if not self.valid_uri(item.get_uri()): return
        path = realpath(gnomevfs.get_local_path_from_uri(item.get_uri()))
        self.nautilusVFSFile_table[path] = item
        
        # TODO:
        return []
    
    #=== HELPER FUNCTIONS ======================================================
    
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
    
    def set_emblem_by_path(self, path):
        """
        Set the emblem for a path (looks up the status in C{statuses}).
        
        @type   path: string
        @param  path: The path for which to set the emblem.
        
        @rtype:       boolean
        @return:      Whether the emblem was set successfully.
        """
        
        # Try and lookup the NautilusVFSFile in the lookup table since 
        # we need it.
        if not path in self.statuses: return False
        if not path in self.nautilusVFSFile_table: return False
        item = self.nautilusVFSFile_table[path]
        
        statuses = self.statuses[path]
        summarized_status = get_summarized_status(path, statuses)
        
        if summarized_status in self.EMBLEMS:
            item.add_emblem(self.EMBLEMS[summarized_status])
            return True
            
        return False
        
    #=== CALLBACKS =============================================================
    
    def cb_status(self, path, statuses):
        """
        This is the callback that C{StatusMonitor} calls. 
        
        @type   path:   string
        @param  path:   The path of the item something interesting happend to.
        
        @type   statuses: tuple of (path, status)
        @param  statuses: 
        """
        
        # We might not have a NautilusVFSFile (which we need to apply an
        # emblem) but we can already store the status for when we do.
        self.statuses[path] = statuses
        
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # We need to invalidate the extension info for only one reason:
        #
        # - Invalidating the extension info will cause Nautilus to remove all
        #   temporary emblems we applied so we don't have overlay problems
        #   (with ourselves, we'd still have some with other extensions).
        #
        # After invalidating C{update_file_info} applies the correct emblem.
        item.invalidate_extension_info()
