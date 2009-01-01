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

"""

Our module for everything related to the Nautilus extension.

Known issues:

  - Emblems sometimes don't update untill the selection is modified.
  
    This is caused by threading problems. There's a bunch of FIXME's below 
    with more information.

  - Multiple emblems are attached to a single item which leads to the one
    obscuring the other. So if an item has "normal" status, but it changes to 
    "modified" two emblems are applied and only the emblem "normal" is visible.
    
    How to reproduce:
    
    You need a working copy with at least 2 items (combination doesn't matter).
    
    Use the following working copy (do not open it in Nautilus before doing this):::
    
        mkdir -p /tmp/nautilussvn_testing
        cd /tmp/nautilussvn_testing
        svnadmin create repository
        svn co file:///tmp/nautilussvn_testing/repository working_copy
        touch working_copy/add-this-file
        touch working_copy/or-this-file
    
    Then after adding one of the files move up the tree so you can see the 
    status for the working_copy directory.
  
    Things I researched but weren't the cause (so don't look into these!):
    
      - One idea I had was that because of the C{nautilusVFSFile_table} we might
        have two seperate C{NautilusVFSFile} instances (with different emblems
        attached) pointing to the same file. But that wasn't the case.
  
"""

# TODO: right before releasing move the commentary above to an actual issue 
# report on the tracker and just refer to the Bug #.

import os.path

import gnomevfs
import nautilus

from nautilussvn.lib.vcs import VCSStatusMonitor
from nautilussvn.lib.extensions.nautilus.vcs import get_vcs_emblems
from nautilussvn.lib.helper import split_path

from nautilussvn.lib.extensions.nautilus.vcs.svn import SVNMainContextMenu

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ 
    This is the main class that implements all of our awesome features.
    
    """
    
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
    #: we also add C{NautilusVFSFile}s to this table from C{get_file_items} etc.
    nautilusVFSFile_table = {}
    
    #: Keep track of item statuses. This is a workaround for the fact that
    #: emblems added using C{NautilusVFSFile.add_emblem} are removed once the 
    #: C{NautilusVFSFile} is invalidated (one example of when this happens is
    #: when an item is modified).::
    #: 
    #:     statuses = {
    #:         "/foo/bar/baz": "modified"
    #:     }
    #: 
    statuses = {}
    
    def __init__(self):
        # Create a StatusMonitor and register a callback with it to notify us 
        # of any status changes.
        self.vcs_status_monitor = VCSStatusMonitor(self.cb_status)
        
    def get_columns(self):
        """
        
        
        """
        
        pass
        
    def update_file_info(self, item):
        """
        
        Normally this function is used to monitor changes to items, however 
        we're using our own C{StatusMonitor} for this. So this function is only
        used to apply emblems (which is needed because emblems from extensions
        are temporary).
        
        C{update_file_info} is called only when:
        
          - When you enter a directory (once for each item) but only when the
            item was modified since the last time it was listed
          - When an item viewable from the current window is created or modified
          
        This is insufficient for our purpose because:
        
          - You're not notified about items you don't see (which is needed to 
            keep the emblem for the directories above the item up-to-date)
        
        When C{update_file_info} is called we do:
        
          - Add the C{NautilusVFSFile} to the lookup table for lookups
          - Add a watch for this item to the C{StatusMonitor} (it's 
            C{StatusMonitor}'s responsibility to check whether this is needed)
        
        What we do to stay up-to-date is:
        
          - We'll notify C{StatusMonitor} of versioning actions (add, commit, lock, 
            unlock etc.), we register callbacks with dialogs for this
        
        When C{StatusMonitor} calls us back we just look the C{NautilusVFSFile} up in
        the look up table using the path and apply an emblem according to the 
        status we've been given.
        
        FIXME: This function is in a race condition with the StatusMonitor
        (which is threaded) to make things update the emblem. For now this
        doesn't seem to be causing any problems (but that doesn't mean anything).
        
        We'll probably have to look into locking and all that stuff.
        
        @type   item: NautilusVFSFile
        @param  item: 
        
        """
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        # Begin debugging code
        print "Debug: update_file_info() called for %s" % path
        # End debugging code
        
        # Always replace the item in the table with the one we receive, because
        # for example if an item is deleted and recreated the NautilusVFSFile
        # we had before will be invalid (think pointers and such).
        self.nautilusVFSFile_table[path] = item
        
        # See comment for variable: statuses
        if path in self.statuses:
            self.set_emblem_by_status(path, self.statuses[path])
            
        self.vcs_status_monitor.add_watch(path)
        
    def get_file_items(self, window, items):
        """
        Menu activated with items selected.
        
        Note that calling C{nautilusVFSFile.invalidate_extension_info()} will 
        also cause get_file_items to be called.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   items:  list of NautilusVFSFile
        @param  items:
        
        @rtype:         list of MenuItems
        @return:        The context menu entries to add to the menu.
        
        """
        
        if len(items) == 0: return
        
        paths = []
        for item in items:
            if item.get_uri().startswith("file://"):
                path = gnomevfs.get_local_path_from_uri(item.get_uri())
                paths.append(path)
                self.nautilusVFSFile_table[path] = item
        
        return SVNMainContextMenu(paths, self).construct_menu()
        
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
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        # Begin debugging code
        print "Debug: get_background_items() for %s" % path
        # End debugging code
        
        self.nautilusVFSFile_table[path] = item
        
        # FIXME:
        # This is a hack to try and work around the multiple emblems on a single
        # item bug. Since get_background_items is called once when you enter
        # a directory we just invalidate all items immediately below it.
        
        # MARKER: performance 
        parent_path = split_path(path)
        if parent_path in self.nautilusVFSFile_table:
            item = self.nautilusVFSFile_table[parent_path]
            item.invalidate_extension_info()
        
        for child_basename in os.listdir(path):
            child_path = os.path.join(path, child_basename)
            if child_path in self.nautilusVFSFile_table:
                # Begin debugging code
                print "Debug: invalidated %s in get_background_items()" % child_basename
                # End debugging code
                child_item = self.nautilusVFSFile_table[child_path]
                # FIXME: still doesn't work but committing to save
                child_item.invalidate_extension_info()
        
        return SVNMainContextMenu([path], self).construct_menu()
    
    #
    # Helper functions
    #
    
    def set_emblem_by_status(self, path, status):
        """
        Set the emblem for a path by status. 
        
        @type   path: string
        @param  path: The path for which to set the emblem.
        
        @type   status: string
        @param  status: A string indicating the status of an item (see: EMBLEMS).
        """
        
        # Try and lookup the NautilusVFSFile in the lookup table since we need it
        # TODO: should we remove this? This function is only called by 
        # update_file_info so this should be guaranteed.
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # Begin debugging code
        #~ print "Debug: set_emblem_by_status() called for %s with status %s" % (path, status)
        # End debugging code
        
        emblems = get_vcs_emblems(path)
        if status in emblems:
            item.add_emblem(emblems[status])
    
    #
    # Callbacks
    #
    
    def cb_status(self, path, status):
        """
        This is the callback that C{StatusMonitor} calls. 
        
        @type   path: string
        @param  path: The path of the item something interesting happend to.
        
        @type   status: string
        @param  status: A string indicating the status of an item (see: EMBLEMS).
        """
        
        # Begin debugging code
        print "Debug: cb_status() called for %s with status %s" % (path, status)
        # End debugging code
        
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # See comment for variable: statuses
        # There's no reason to do a lot of stuff if the emblem is the same
        # but since we're the only function who does a add_emblem, we have to.
        
        self.statuses[path] = status
        
        # We need to invalidate the extension info for only one reason:
        #
        # - Invalidating the extension info will cause Nautilus to remove all
        #   temporary emblems we applied so we don't have overlay problems
        #   (with ourselves, we'd still have some with other extensions).
        #
        # FIXME: for some reason the invalidate_extension_info isn't always 
        # processed and update_file_info isn't called. So as a workaround we
        # already set the emblem, running the risk of applying multiple emblems
        # at the same time which overlap potentially resulting in the actual 
        # status of an item not being displayed.
        #
        self.set_emblem_by_status(path, status)
        item.invalidate_extension_info()



