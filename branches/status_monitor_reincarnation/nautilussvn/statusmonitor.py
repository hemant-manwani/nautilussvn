import os
from os.path import isdir, isfile, realpath, basename
import time

import gobject
import gio

import anyvc
from anyvc.workdir import get_workdir_manager_for_path

from nautilussvn.util.decorators import timeit, disable

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
    
    @timeit
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
        
        @type   path:   list
        @param  path:   A list of (abspath, state) tuples
        """
        
        # Unlike Subversion most VCS's don't have the concept of statuses
        # on directories, so make sure to take this into account.
        # FIXME: but why are we doing this:
        statuses = [(status[0], status[1]) for status in statuses if status[0].startswith(path)]
        text_statuses = [status[1] for status in statuses]
        statuses_dictionary = dict(statuses)
        
        # If no statuses are returned but we do have a workdir_manager
        # it means that an error occured, most likely a working copy
        # administration area (.svn directory) went missing but it could
        # be pretty much anything.
        if not statuses: 
            # FIXME: figure out a way to make only the directory that
            # is missing display conflicted and the rest unkown.
            return "unknown"

        # We need to take special care of directories
        if isdir(path):
            # These statuses take precedence.
            if "conflicted" in text_statuses: return "conflicted"
            if "obstructed" in text_statuses: return "obstructed"
            
            # The following statuses take precedence over the status
            # of children.
            if (path in statuses_dictionary and 
                    statuses_dictionary[path] in ["added", "modified", "deleted"]):
                return statuses_dictionary[path]
            
            # A directory should have a modified status when any of its children
            # have a certain status (see modified_statuses above). Jason thought up 
            # of a nifty way to do this by using sets and the bitwise AND operator (&).
            if len(set(self.MODIFIED_STATUSES) & set(text_statuses)):
                return "modified"
        
        # If we're not a directory we end up here.
        if path in statuses_dictionary: return statuses_dictionary[path]
        return "normal"
        
    def process_event(self, monitor, file, other_file, event_type):
        # Ignore any events we're not interested in
        # FIXME: creating a file will fire both CHANGES_DONE and EVENT_CREATED
        # so it's probably a good idea to throttle.
        # FIXME: what about gio.FILE_MONITOR_EVENT_DELETED?
        if event_type not in (gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT, 
            gio.FILE_MONITOR_EVENT_CREATED): return
        
        path = file.get_path()
        
        # Some of the files we should ignore
        # When using SVN the administration area is modified a lot, but 
        # only the entries file really matters.
        if path.find(".svn") != -1 and not path.endswith(".svn/entries"): return
        if path.find(".git") != -1: return # FIXME: not handling Git right now
        
        print path, event_type
        
        # TODO: if we can actually figure out specifically what file was
        # changed by looking at the entries file this would be a lot easier
        parent_dir = None
        if path.endswith(".svn/entries"):
            parent_dir = working_dir = os.path.abspath(os.path.join(os.path.dirname(path), ".."))
            paths = [os.path.join(working_dir, basename) for basename in os.listdir(working_dir)]
            for path in paths:
                self.status(path, invalidate=True, recursive=False)
        else:
            # Let's try and do some fancy stuff to detect if we were 
            # dealing with an unversioned file, this is a little bit
            # hard because like mentioned before, Subversion is one of
            # the few VCS's where directories actually matter.
            workdir_manager = get_workdir_manager_for_path(path)
            statuses_dictionary = dict([
                (status.abspath, status.state) 
                for status in workdir_manager.status(paths=(path,), recursive=False)
                if status.state != "unknown"
            ])
            
            if isdir(path) or path in statuses_dictionary:
                self.status(path, invalidate=True, recursive=False)
                parent_dir = os.path.split(path)[0]
        
        # Refresh the status for all parents
        if parent_dir:
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
    
    @timeit
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
                        # FIXME: stupid temporary files that get create on vcs
                        # operations and whatnot, I don't know to handle these
                        # properly yet 
                        try:
                            statuses = [(status.abspath, status.state) for status in 
                                workdir_manager.status(paths=(path,), recursive=recursive)]
                            self.update_status_tree(statuses)
                        except OSError:
                            pass
                    
                    status = self.get_text_status(path, statuses)
                    self.status_callback(path, status)
                    
            self.status_queue_is_active = False
            return False
            
        return True

    def update_status_tree(self, statuses):
        for path, status in statuses:
            self.status_tree[path] = status
