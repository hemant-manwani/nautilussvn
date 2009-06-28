"""

"""

import threading
from Queue import Queue

from __future__ import with_statement

import pysvn

class StatusChecker(threading.Thread):
    """ 
    Represents our status checking 'peon' thread.
    """
    
    #: The queue will be populated with 4-ples of
    #: (path, recurse, invalidate, callback).
    __paths_to_check = Queue()
    
    #: This tree stores the status of the items. We monitor working copies
    #: for changes and modify this tree in-place accordingly. This way
    #: we don't have to do any intensive status checks apart from the initial
    #: one and the speed is increased because the tree is in memory.
    __status_tree = dict()
    
    #: Need a re-entrant lock here, look at check_status/add_path_to_check
    __status_tree_lock = threading.RLock()

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.vcs_client = pysvn.Client()
        
        # This means that the thread will die when everything else does. If
        # there are problems, we will need to add a flag to manually kill it.
        self.setDaemon(True)
        
    def check_status(self, path, recurse=False, invalidate=False, callback=None):
        """
        Checks the status of the given path. Must be thread safe. Unless
        specified, if the path is not in the stored status tree, we add it to
        the list of things to look up.
        
        This can go two ways:
        
          1. If we've already looked the path up, return the statuses associated
             with it. This will block for as long as any other thread has our
             status_tree locked.
        
          2. If we haven't already got the path, return "None" (can change this
             if necessary). This will also block for max of (1) as long as the
             status_tree is locked OR if the queue is blocking. In the meantime,
             the thread will pop the path from the queue and look it up.
        """
        with self.__status_tree_lock:
            if path in self.__status_tree:
                statuses = self.__get_path_statuses(path)
            else:
                statuses = None
                self.add_path_to_check(path, recurse, invalidate, callback)
        
        return statuses
    
    def add_path_to_check(self, path, recurse=False, invalidate=False, callback=None):
        """
        This adds a file to have its status checked. Note that we remove this
        path from the status tree.
        
        """
        with self.__status_tree_lock:
            if path in self.__status_tree:
                # Also need to sort this out for different data structure.
                del self.__status_tree[path]
        
        # Like this:
        # callback(path, [STATUS.CALCULATING])
        self.__paths_to_check.put((path, recurse, invalidate, callback))        
        
    def run(self):
        """
        Overrides the run method from Thread, so do not put any arguments in
        here.
        """
        
        # This loop will stop when the thread is killed, which it will 
        # because it is daemonic.
        while True:
            # This call will block if the Queue is empty, until something is
            # added to it. There is a better way to do this if we need to add
            # other flags to this.
            (path, recurse, invalidate, callback) = self.__paths_to_check.get()
            self.__update_path_status(path, recurse, invalidate, callback)
    
    def __get_path_statuses(self, path)
        with self.__status_tree_lock:
            # Need to change this for different structure.
            statuses = __status_tree[path]
        
        return statuses
        
    def __update_path_status(self, path, recurse=False, invalidate=False, callback=None):
        """
        
        """
        
        do_status_check = False
        statuses = []
        
        with self.__status_tree_lock:
            do_status_check = invalidate or path not in self.__status_tree
            # If we're not doing the status check, get the cached results NOW,
            # in case they are deleted during the next statement
            # DO NOT USE check_status
            if not do_status_check:
                statuses = self.__get_path_statuses(path)
        
        if do_status_check:
            statuses = self.vcs_client.status(path, recurse=recurse)

        with self.__status_tree_lock:
            for another_path in self.__status_tree.keys():
                if another_path.startswith(path):
                    statuses.append((another_path, self.__status_tree[another_path]))
            self.__update_status_tree(
                [(status.path, str(status.text_status)) for status in statuses]
            )

        # Remember: these callbacks will block THIS thread from calculating the
        # next path on the "to do" list.
        if callback: callback(path, statuses)
        
    def __update_status_tree(self, statuses):
        with self.__status_tree_lock:
            for path, status in statuses:
                self.__status_tree[path] = status
