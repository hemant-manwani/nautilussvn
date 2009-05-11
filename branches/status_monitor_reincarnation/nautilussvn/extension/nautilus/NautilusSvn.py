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
        "obstructed":   "nautilussvn-obstructed"
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
        print "Initializing nautilussvn extension"
        self.status_monitor = StatusMonitor(
            watch_callback=self.cb_watch_added,
            status_callback=self.cb_status
        )
    
    @timeit
    def update_file_info(self, item):
        """
        
        Normally this function is used to monitor changes to items, however 
        we're using our own C{StatusMonitor} for this. So this function is only
        used to apply emblems (which is needed because emblems from extensions
        are temporary).
        
        C{update_file_info} is called only when:
        
          - When you enter a directory (once for each item but only when the
            item was modified since the last time it was listed)
          - When you refresh (once for each item visible)
          - When an item viewable from the current window is created or modified
          
        This is insufficient for our purpose because:
        
          - You're not notified about items you don't see (which is needed to 
            keep the emblem for the directories above the item up-to-date)
            
        When C{update_file_info} is called we do:
        
          - Add the C{NautilusVFSFile} to the lookup table for lookups
          - Add a watch for this item to the C{StatusMonitor} (it's 
            C{StatusMonitor}'s responsibility to check whether this is needed)
            
        When C{StatusMonitor} calls us back we just look the C{NautilusVFSFile} up in
        the look up table using the path and apply an emblem according to the 
        status we've been given.
        
        @type   item: NautilusVFSFile
        @param  item: 
        
        """
        
        if not self.valid_uri(item.get_uri()): return
        path = realpath(gnomevfs.get_local_path_from_uri(item.get_uri()))
        
        # Always replace the item in the table with the one we receive, because
        # for example if an item is deleted and recreated the NautilusVFSFile
        # we had before will be invalid (think pointers and such).
        self.nautilusVFSFile_table[path] = item
        
        # We don't have to do anything else since it's already clear
        # that the StatusMonitor is aware of this item.
        if self.set_emblem_by_path(path): return
        
        # Since update_file_info is also the function which lets us
        # know when we see a particular item for the first time we have
        # to figure out whether or not we should do a status check.
        has_watch = self.status_monitor.has_watch(path)
        is_in_a_or_a_working_copy = get_workdir_manager_for_path(path)
        
        if not has_watch and is_in_a_or_a_working_copy:
            self.status_monitor.add_watch(path)
            
        # If we access the StatusMonitor over DBus it keeps running even though 
        # Nautilus is not. So watches will stay attached. So an initial status 
        # check won't be done. Though there are other situations where there is
        # a watch but we don't have a status yet.
        elif (has_watch and
                not path in self.statuses and
                is_in_a_or_a_working_copy):
            self.status_monitor.status(path)
    
    def get_file_items(self, window, items):
        """
        Menu activated with items selected. Nautilus also calls this function
        when rendering submenus, even though this is not needed since the entire
        menu has already been returned.
        
        Note that calling C{nautilusVFSFile.invalidate_extension_info()} will 
        also cause get_file_items to be called.
        
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
    
    #
    # Helper functions
    #
    
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
        
        status = self.statuses[path]
        
        if status in self.EMBLEMS:
            item.add_emblem(self.EMBLEMS[status])
            return True
            
        return False
        
    #
    # Callbacks
    #
    
    def cb_watch_added(self, path):
        """
        This callback is called by C{StatusMonitor} when a watch is added
        for a particular path.
        
        @type   path:   string
        @param  path:   The path for which a watch was added
        """
        
        self.status_monitor.status(path)
    
    def cb_status(self, path, status):
        """
        This is the callback that C{StatusMonitor} calls. 
        
        @type   path:   string
        @param  path:   The path of the item something interesting happend to.
        
        @type   status: string
        @param  status: A string indicating the status of an item (see: EMBLEMS).
        """
        
        # We might not have a NautilusVFSFile (which we need to apply an
        # emblem) but we can already store the status for when we do.
        self.statuses[path] = status

        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # We need to invalidate the extension info for only one reason:
        #
        # - Invalidating the extension info will cause Nautilus to remove all
        #   temporary emblems we applied so we don't have overlay problems
        #   (with ourselves, we'd still have some with other extensions).
        #
        # After invalidating update_file_info applies the correct emblem.
        #
        # FIXME: added set_emblem_by_path_call because Nautilus doesn't
        # seem to invalidate the extension info
        self.set_emblem_by_path(path)
        item.invalidate_extension_info()

import time

import gobject
import gio

class StatusMonitor:
    """
    
    The C{StatusMonitor} is basically a replacement for the currently limited 
    C{update_file_info} function. 
    
    What C{StatusMonitor} does:
    
      - When somebody adds a watch and if there's not already a watch for this 
        item it will add one.
    
      - Use gio.FileMonitor to keep track of modifications of any watched items.
        
      - Either on request, or when something interesting happens, it checks
        the status for an item which means:
        
          - See C{status) for exactly what a status check means.
    
    UML sequence diagram depicting how the StatusMonitor is used::

        +---------------+          +-----------------+         
        |  NautilusSVN  |          |  StatusMonitor  |         
        +---------------+          +-----------------+         
               |                            |
               |   new(self.cb_status)      |
               |--------------------------->|
               |                            |
               |     add_watch(path)        |
               |--------------------------->|
               |                            |
               |      watch_added(path)     |
               |<---------------------------|
               |                            |
               |        status(path)        |
               |--------------------------->|
               |                            |
               |  cb_status(path, status)   |
               |<---------------------------|
               |                            |
               |---+                        |
               |   | set_emblem_for_path(path)
               |<--+                        |
               |                            |
    
    """
    
    #: A list of statuses which count as modified (for a directory) in 
    #: TortoiseSVN emblem speak.
    MODIFIED_STATUSES = [
        "added",
        "deleted",
        "replaced",
        "modified",
        "missing"
    ]
    
    #: A list to keep track of the paths we're watching.
    #: 
    #: It looks like:::
    #:
    #:     watches = [
    #:         "/foo/bar/baz"
    #:     ]
    #:     
    watches = []
    
    #: This is a queue to make sure status checks are done in a orderly
    #: manner. It hasn't been completely implemented yet (and I'm wondering
    #: if it's really necessary, but ok).
    status_queue = []
    status_queue_last_accessed = None
    status_queue_is_active = False
    
    STATUS_QUEUE_TIMEOUT = 100
    STATUS_QUEUE_PROCESS_TIMEOUT = 100
    
    #: This tree stores the status of the items. We monitor working copy
    #: for changes and modify this tree in-place accordingly. This way
    #: apart from an intial recursive check we don't have to do any
    #: and the speed is increased because the tree is in memory.
    #:
    #: This isn't a tree (yet) and looks like:::
    #:
    #:     status_tree = {
    #:         "/foo": "normal",
    #:         "/foo/bar": normal",
    #:         "/foo/bar/baz": "added"
    #:     }
    #:
    #: As you can see it's not a tree (yet) and the way statuses are 
    #: collected as by iterating through the dictionary. This is 
    #: obviously going to cause issues once the user has collected a 
    #: great deal of paths.
    status_tree = {}
    
    def __init__(self, watch_callback, status_callback):
        self.watch_callback = watch_callback
        self.status_callback = status_callback
    
    def has_watch(self, path):
        return (path in self.watches)
    
    def add_watch(self, path):
        """
        Request a watch to be added for path. This function will figure out
        the best spot to add the watch (most likely a parent directory).
        
        It's only interesting to add a watch for what we think the user
        may actually be looking at.
        """
        
        # Check whether or not a watch is already added
        path_to_check = path
        watch_is_already_set = False
        while path_to_check != "/":
            if path_to_check in self.watches:
                watch_is_already_set = True
                break;
                
            path_to_check = os.path.split(path_to_check)[0]
        
        # If not, figure out where the watch should be added
        if not watch_is_already_set:
            path_to_check = path
            path_to_attach = path
            while path_to_check != "/":    
                path_to_check = os.path.split(path_to_check)[0]
                if get_workdir_manager_for_path(path_to_check):
                    path_to_attach = path_to_check
                    break;
            
            # And actually register the watches
            self.register_watches(path_to_attach)
            
        # TODO: should we always call the client back even if a watch
        # wasn't attached?
        if path not in self.watches: self.watches.append(path)
        self.watch_callback(path)
    
    def register_watches(self, path):
        """
        Recursively add watches to all directories.
        """
        
        paths_to_attach = [path]
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                paths_to_attach.append(os.path.join(root, dir))
        
        for path_to_attach in paths_to_attach:
            if path_to_attach not in self.watches:
                self.watches.append(path_to_attach)
                file = gio.File(path_to_attach)
                monitor = file.monitor_directory()
                monitor.connect("changed", self.process_event)
        
    def status(self, path, invalidate=False, recursive=True):
        self.add_to_queue(path, invalidate=invalidate, recursive=recursive)

    def get_text_status(self, path, statuses):
        """
        This is a helper function to figure out the textual representation 
        for a set of statuses. In TortoiseSVN speak a directory is
        regarded as modified when any of its children are either added, 
        deleted, replaced, modified or missing so you can quickly see if 
        your working copy has local changes.
        """
        
        text_statuses = [status[1] for status in statuses]
        
        # If no statuses are returned but we do have a workdir_manager
        # it means that an error occured, most likely a working copy
        # administration area (.svn directory) went missing
        if not text_statuses: 
            # FIXME: figure out a way to make only the directory that
            # is missing display conflicted and the rest unkown.
            return "conflicted"

        # We need to take special care of directories
        if isdir(path):
            # These statuses take precedence.
            if "conflicted" in text_statuses: return "conflicted"
            if "obstructed" in text_statuses: return "obstructed"
            
            # The following statuses take precedence over the status
            # of children.
            if text_statuses[0] in ["added", "modified", "deleted"]:
                return text_statuses[0]
            
            # A directory should have a modified status when any of its children
            # have a certain status (see modified_statuses above). Jason thought up 
            # of a nifty way to do this by using sets and the bitwise AND operator (&).
            if len(set(self.MODIFIED_STATUSES) & set(text_statuses[1:])):
                return "modified"
        
        # If we're not a directory we end up here.
        return text_statuses[0]
        
    def process_event(self, monitor, file, other_file, event_type):
        # Ignore any events we're not interested in
        # FIXME: creating a file will fire both CHANGES_DONE and EVENT_CREATED
        # so it's probably a good idea to throttle.
        if event_type not in (gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT, 
            gio.FILE_MONITOR_EVENT_DELETED,
            gio.FILE_MONITOR_EVENT_CREATED): return
        
        path = file.get_path()
        
        # Some of the files we should ignore
        # For SVN the administration area is modified a lot, but only the 
        # entries file really matters.
        if path.find(".svn") != -1 and not path.endswith(".svn/entries"): return
        if path.find(".git") != -1: return
        
        print os.path.basename(path), event_type
        
        # TODO: if we can actually figure out specifically what file was
        # changed by looking at the entries file this would be a lot easier
        parent_dir = ""
        if path.endswith(".svn/entries"):
            parent_dir = working_dir = os.path.abspath(os.path.join(os.path.dirname(path), ".."))
            paths = [os.path.join(working_dir, basename) for basename in os.listdir(working_dir)]
            for path in paths:
                # FIXME: this ignores propchanges for the moment
                if not isdir(path): 
                    self.status(path, invalidate=True, recursive=False)
        else:
            parent_dir = os.path.split(path)[0]
            self.status(path, invalidate=True, recursive=False)
        
        # Refresh the status for all parents
        path_to_check = parent_dir
        while path_to_check != "/":
            if not get_workdir_manager_for_path(path_to_check): break
            self.status(path_to_check, recursive=False)
            path_to_check = os.path.split(path_to_check)[0]
    
    def add_to_queue(self, path, invalidate, recursive):
        if (path, invalidate, recursive) in self.status_queue: return
        print "added %s to queue" % path
        self.status_queue.append((path, invalidate, recursive))
        self.status_queue_last_accessed = time.time()
        
        # Register a timeout handler to start processing the queue
        if not self.status_queue_is_active:
            self.status_queue_is_active = True
            gobject.timeout_add(self.STATUS_QUEUE_TIMEOUT, self.process_queue)
        
    def process_queue(self):
        if (time.time() - self.status_queue_last_accessed) > (self.STATUS_QUEUE_PROCESS_TIMEOUT / 1000):
            print "processing queue"
            # FIXME: this is a temporary hack to make sure that lower 
            # files are checked before the directories are (so status is
            # figured out correctly. 
            self.status_queue.sort(reverse=True)
            
            while len(self.status_queue) > 0:
                path, invalidate, recursive = self.status_queue.pop(0)
                workdir_manager = get_workdir_manager_for_path(path)
                if workdir_manager:
                    statuses = []
                    print "processing %s" % path
                    # Let's take a look and see if we have already collected
                    # this path previously, if so no need to actually try
                    # and found out the status
                    if not invalidate and path in self.status_tree:
                        for another_path in self.status_tree.keys():
                            if another_path.startswith(path):
                                statuses.append((another_path, self.status_tree[another_path]))
                    else:
                        # It wasn't in the tree or an invalidation was
                        # requested so let's do the status check
                        statuses = [(status.abspath, status.state) for status in 
                            workdir_manager.status(paths=(path,), recursive=recursive)]
                        self.update_status_tree(statuses)
                    
                    status = self.get_text_status(path, statuses)
                    self.status_callback(path, status)
                    
            self.status_queue_is_active = False
            return False
            
        return True

    def update_status_tree(self, statuses):
        for path, status in statuses:
            self.status_tree[path] = status
