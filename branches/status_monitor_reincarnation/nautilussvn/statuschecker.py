import time

import gobject

from anyvc.workdir import get_workdir_manager_for_path

from nautilussvn.util.decorators import timeit, disable

class StatusChecker:
    
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
    
    def status(self, paths=(), invalidate=False, recursive=True, status_callback=None):
        self.add_to_queue(paths, invalidate=invalidate, recursive=recursive, status_callback=status_callback)
    
    def add_to_queue(self, paths, invalidate, recursive, status_callback):
        if (paths, invalidate, recursive, status_callback) in self.status_queue: return
        print "added %s to queue" % paths
        self.status_queue.append((paths, invalidate, recursive, status_callback))
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
                paths, invalidate, recursive, status_callback = self.status_queue.pop(0)
                
                for path in paths:
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
                        
                # Call the client back with the results
                results = []
                for path in paths:
                    for another_path in self.status_tree.keys():
                        if another_path.startswith(path):
                            results.append((another_path, self.status_tree[another_path]))
                status_callback(paths, results)
                    
            self.status_queue_is_active = False
            return False
            
        return True

    def update_status_tree(self, statuses):
        for path, status in statuses:
            self.status_tree[path] = status
