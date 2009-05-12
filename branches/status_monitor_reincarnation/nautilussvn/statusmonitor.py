import os
from os.path import isdir, isfile, realpath, basename

import gio

from anyvc.workdir import get_workdir_manager_for_path

from nautilussvn.statuschecker import StatusChecker
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
    
    #: A list to keep track of the paths we're watching.
    #: 
    #: It looks like:::
    #:
    #:     watches = [
    #:         "/foo/bar/baz"
    #:     ]
    #:     
    watches = []
    
    def __init__(self, watch_callback, status_callback):
        # The callbacks
        self.watch_callback = watch_callback
        
        # Create a status checker we can use to request status checks
        self.status_checker = StatusChecker(
            status_callback=status_callback
        )
    
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
                self.status_checker.status(path, invalidate=True, recursive=False)
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
                self.status_checker.status(path, invalidate=True, recursive=False)
                parent_dir = os.path.split(path)[0]
        
        # Refresh the status for all parents
        if parent_dir:
            path_to_check = parent_dir
            while path_to_check != "/":
                if not get_workdir_manager_for_path(path_to_check): break
                self.status_checker.status(path_to_check, recursive=False)
                path_to_check = os.path.split(path_to_check)[0]
