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

Concrete VCS implementation for Subversion functionality.

"""

import os.path
from os.path import isdir, isfile

import pysvn
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

from nautilussvn.lib.decorators import deprecated, timeit
from nautilussvn.lib.helper import split_path

class SVN:
    
    STATUS = {
        "none"          : pysvn.wc_status_kind.none,
        "unversioned"   : pysvn.wc_status_kind.unversioned,
        "normal"        : pysvn.wc_status_kind.normal,
        "added"         : pysvn.wc_status_kind.added,
        "missing"       : pysvn.wc_status_kind.missing,
        "deleted"       : pysvn.wc_status_kind.deleted,
        "replaced"      : pysvn.wc_status_kind.replaced,
        "modified"      : pysvn.wc_status_kind.modified,
        "merged"        : pysvn.wc_status_kind.merged,
        "conflicted"    : pysvn.wc_status_kind.conflicted,
        "ignored"       : pysvn.wc_status_kind.ignored,
        "obstructed"    : pysvn.wc_status_kind.obstructed,
        "external"      : pysvn.wc_status_kind.external,
        "incomplete"    : pysvn.wc_status_kind.incomplete
    }

    STATUSES_FOR_COMMIT = [
        STATUS["unversioned"],
        STATUS["added"],
        STATUS["deleted"],
        STATUS["replaced"],
        STATUS["modified"],
    ]
    
    STATUSES_FOR_ADD = [
        STATUS["unversioned"]
    ]
    
    PROPERTIES = {
        "executable":   "svn:executable",
        "mime-type":    "svn:mime-type",
        "ignore":       "svn:ignore",
        "keywords":     "svn:keywords",
        "eol-style":    "svn:eol-style",
        "externals":    "svn:externals",
        "special":      "svn:special"
    }
    
    NOTIFY_ACTIONS = {
        pysvn.wc_notify_action.add:                     "Added",
        pysvn.wc_notify_action.copy:                    "Copied",
        pysvn.wc_notify_action.delete:                  "Deleted",
        pysvn.wc_notify_action.restore:                 "Restored",
        pysvn.wc_notify_action.revert:                  "Reverted",
        pysvn.wc_notify_action.failed_revert:           "Failed Revert",
        pysvn.wc_notify_action.resolved:                "Resolved",
        pysvn.wc_notify_action.skip:                    "Skipped",
        pysvn.wc_notify_action.update_delete:           "Deleted",
        pysvn.wc_notify_action.update_add:              "Added",
        pysvn.wc_notify_action.update_update:           "Updated",
        pysvn.wc_notify_action.update_completed:        "Completed",
        pysvn.wc_notify_action.update_external:         "External",
        pysvn.wc_notify_action.status_completed:        "Completed",
        pysvn.wc_notify_action.status_external:         "External",
        pysvn.wc_notify_action.commit_modified:         "Modified",
        pysvn.wc_notify_action.commit_added:            "Added",
        pysvn.wc_notify_action.commit_deleted:          "Copied",
        pysvn.wc_notify_action.commit_replaced:         "Replaced",
        pysvn.wc_notify_action.commit_postfix_txdelta:  "Changed",
        pysvn.wc_notify_action.annotate_revision:       "Annotated",
        pysvn.wc_notify_action.locked:                  "Locked",
        pysvn.wc_notify_action.unlocked:                "Unlocked",
        pysvn.wc_notify_action.failed_lock:             "Failed Lock",
        pysvn.wc_notify_action.failed_unlock:           "Failed Unlock"
    }
    
    NOTIFY_ACTIONS_COMPLETE = [
        pysvn.wc_notify_action.status_completed,
        pysvn.wc_notify_action.update_completed        
    ]
    
    NOTIFY_STATES = {
        pysvn.wc_notify_state.inapplicable:             "Inapplicable",
        pysvn.wc_notify_state.unknown:                  "Unknown",
        pysvn.wc_notify_state.unchanged:                "Unchanged",
        pysvn.wc_notify_state.missing:                  "Missing",
        pysvn.wc_notify_state.obstructed:               "Obstructed",
        pysvn.wc_notify_state.changed:                  "Changed",
        pysvn.wc_notify_state.merged:                   "Merged",
        pysvn.wc_notify_state.conflicted:               "Conflicted"
    }
    
    REVISIONS = {
        "unspecified":      pysvn.opt_revision_kind.unspecified,
        "number":           pysvn.opt_revision_kind.number,
        "date":             pysvn.opt_revision_kind.date,
        "committed":        pysvn.opt_revision_kind.committed,
        "previous":         pysvn.opt_revision_kind.previous,
        "working":          pysvn.opt_revision_kind.working,
        "head":             pysvn.opt_revision_kind.head
    }
    
    DEPTHS = {
        "empty":        pysvn.depth.empty,
        "exclude":      pysvn.depth.exclude,
        "files":        pysvn.depth.files,
        "immediates":   pysvn.depth.immediates,
        "infinity":     pysvn.depth.infinity,
        "unknown":      pysvn.depth.unknown
    }
    
    DEPTHS_FOR_CHECKOUT = {
        "Fully Recursive":                          DEPTHS["infinity"],
        "Immediate children, including folders":    DEPTHS["immediates"],
        "Only file children":                       DEPTHS["files"],
        "Only this item":                           DEPTHS["empty"]
    }
    
    #: This variable is used to maintain a status cache. Paths function as keys
    #: and every item in the cache has all the statuses for all the items below
    #: it, though the last item is always the status for the path. 
    #: 
    #: It looks like:::
    #:  
    #:     status_cache = {
    #:        "/foo/bar/baz": [<PysvnStatus u'baz'>]
    #:        "/foo/bar": [<PysvnStatus u'baz'>, <PysvnStatus u'bar'>, ]
    #:        "/foo": [<PysvnStatus u'foo'>, <PysvnStatus u'bar'>, <PysvnStatus u'baz'>]
    #:     }
    #:
    #: It is shared over all instances. Don't ask me why though, I don't 
    #: understand how it works myself.
    #:
    status_cache = {}
    
    def __init__(self):
        self.client = pysvn.Client()
    
    def status(self, path, recurse=True, depth=None):
        """
        This function will eventually be deprecated for status_with_cache which
        at the moment is still in flux.
        
        """
        if depth:
            return self.client.status(path, depth=depth)
        else:
            return self.client.status(path, recurse=recurse)
    
    @timeit
    def status_with_cache(self, path, invalidate=False, depth=pysvn.depth.infinity):
        """
        
        Look up the status for path.
        
        If invalidate is set to False this function will look to see if a 
        status for the requested path is available in the cache and if so
        return that. Otherwise it will bypass the cache entirely.
        
        @type   path: string
        @param  path: A path pointing to an item (file or directory).
        
        @type   invalidate: boolean
        @param  invalidate: Whether or not the cache should be bypassed.
        
        @type   depth: one of pysvn.depth
        @param  depth: Defines how deep the status check should go.
        
        @rtype:        list of PysvnStatus
        @return:       A list of statuses for the given path, with the status 
                       for the path being the first item in the list.
        
        """
        
        # FIXME: the len check is a temporary hack untill I think up of something
        # better. It's needed because status checks with a depth of empty are done
        # first for every file, meaning that the following infinity check would
        # otherwise be an inmediate cache hit.
        if (invalidate or 
                path not in self.status_cache or
                len(self.status_cache[path]) == 1):
            print "Debug: status_with_cache() invalidated %s" % path
            # FIXME: the is_ functions call us with an empty depth, that 
            # probably screws something up.
            statuses = self.client.status(path, depth=depth)
        else:
            return self.status_cache[path]
        
        # The next few lines convert a list of PysvnStatus returned by
        # pysvn.Client.status() from:
        #
        #  [<PysvnStatus u'foo/bar/baz'>, 
        #   <PysvnStatus u'foo/bar'>, 
        #   <PysvnStatus u'foo'>]
        #
        # To the one described in the comments for C{status_cache}.
        #

        for status in statuses:
            path_bit = os.path.abspath(os.path.join(path, status.data["path"]))
            
            while path_bit != "":
                if (invalidate or 
                        not path_bit in self.status_cache):
                    self.status_cache[path_bit] = []
                    
                self.status_cache[path_bit].append(status)
                path_bit = split_path(path_bit)
        
        return self.status_cache[path]
    #
    # is
    #
    
    def is_working_copy(self, path):
        try:
            entry = self.client.info(path)
            # when a versioned directory is removed and replaced with a
            # non-versioned directory (one that doesn't have a working copy
            # administration area, or .svn directory) you can't do a status 
            # call on that item itself (results in an exception).
            # 
            # Note that this is not a conflict, it's more of a corruption. 
            # And it's associated with the status "obstructed".
            #
            # TODO: This check doesn't really belong here though.
            #
            if entry:
                if isdir(path) and not isdir(os.path.join(path, ".svn")):
                    return False
            return True
        except pysvn.ClientError, e:
            # FIXME: ClientError client in use on another thread
            print "    Debug: EXCEPTION in is_working_copy(): %s" % str(e)
            return False
        
    def is_in_a_or_a_working_copy(self, path):
        return self.is_working_copy(path)
        
    def is_versioned(self, path):
        # info will return nothing for an unversioned file inside a working copy
        if self.client.info(path):
            return True
        
        return False
    
    def is_normal(self, path):
        status = self.status_with_cache(path, depth=pysvn.depth.empty)[-1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.normal:
            return True
        
        return False
    
    def is_added(self, path):
        status = self.status_with_cache(path, depth=pysvn.depth.empty)[-1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.added:
            return True
        
        return False
        
    def is_modified(self, path):
        status = self.status_with_cache(path, depth=pysvn.depth.empty)[-1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.modified:
            return True
        
        return False
    
    def is_deleted(self, path):
        status = self.status_with_cache(path, depth=pysvn.depth.empty)[-1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.deleted:
            return True
        
        return False
        
    def is_ignored(self, path):
        status = self.status_with_cache(path, depth=pysvn.depth.empty)[-1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.ignored:
            return True
        
        return False
        
        
    #
    # has
    #
    
    def has_unversioned(self, path):
        all_status = self.status_with_cache(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.unversioned:
                return True
                
        return False
    
    def has_added(self, path):
        all_status = self.status_with_cache(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.added:
                return True
                
        return False
        
    def has_modified(self, path):
        all_status = self.status_with_cache(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.modified:
                return True
        
        return False

    def has_deleted(self, path):
        all_status = self.status_with_cache(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.deleted:
                return True
        
        return False
        
        
    #
    # provides information for ui
    #
    
    def get_items(self, paths, statuses=None):
        """
        Retrieves a list of files that have one of a set of statuses
        
        @type   paths:      list
        @param  paths:      A list of paths or files.
        
        @type   statuses:   list
        @param  statuses:   A list of pysvn.wc_status_kind statuses.
        
        @rtype:             list
        @return:            A list of PysvnStatus objects.
        
        """

        if paths is None:
            return []
 
        if len(paths) > 1:
            path = os.path.commonprefix(paths)
        else:
            path = paths[0]
        
        #if the current path is a parent of the given path, cut off the parents
        if path.find(os.getcwd()) != -1:
            path = path[len(os.getcwd())+1:]
        
        #recursively searches the common path of all "paths" item
        st = self.client.status(
            path
        )

        if st is None:
            return []

        returner = []
        for st_item in st:
            if statuses is not None:
                if st_item.text_status not in statuses:
                    continue
                
            returner.append(st_item)
        
        return returner
        
    def get_repo_url(self, path):
        """
        Retrieve the repository URL for the given working copy path
        
        @type   path:   string
        @param  path:   A working copy path.
        
        @rtype:         string
        @return:        A repository URL.
        
        """
        
        info = self.client.info(path)
        
        returner = None
        try:
            returner = info["url"]
        except KeyError, e:
            print "KeyError exception in svn.py get_repo_url()"
            print str(e)
        
        return returner
    
    def get_revision(self, path):
        """
        Retrieve the current revision number for a path
        
        @type   path:   string
        @param  path:   A working copy path.
        
        @rtype:         integer
        @return:        A repository revision.
        
        """
    
        info = self.client.info(path)
        
        returner = None
        try:
            returner = info["revision"].number
        except KeyError, e:
            print "KeyError exception in svn.py get_revision()"
            print str(e)
        except AttributeError, e:
            print "AttributeError exception in svn.py get_revision()"
            print str(e)
        
        return returner
    
    #
    # properties
    #
    
    def proppath(self, path):
        """
        Generates a safe path to use with the prop* functions.
        If the given path is unversioned, go to the next path up.

        @type   path:   string
        @param  path:   A file or directory path.
        
        @rtype:         string
        @return:        A prop* function-safe path.

        """

        st = self.client.status(path)
        if st[0].text_status == self.STATUS["unversioned"]:
            path = os.path.dirname(path)
        
        return path
        
    def propset(self, path, prop_name, prop_value, overwrite=False):
        """
        Adds an svn property to a path.  If the item is unversioned,
        add a recursive property to the parent path
        
        @type   path: string
        @param  path: A file or directory path.
        
        @type   prop_name: string
        @param  prop_name: An svn property name.
        
        @type   prop_value: string
        @param  prop_value: An svn property value/pattern.
        
        """
        
        path = self.proppath(path)

        if overwrite:
            props = prop_value
        else:
            props = self.propget(path, prop_name)
            props = "%s%s" % (props, prop_value)
        
        returner = False
        try:
            self.client.propset(
                prop_name, 
                props, 
                path, 
                recurse=True
            )
            returner = True
        except pysvn.ClientError, e:
            print "pysvn.ClientError exception in svn.py propset()"
            print str(e)
        except TypeError, e:
            print "TypeError exception in svn.py propset()"
            print str(e)
            
        return returner
        
    def proplist(self, path):
        """
        Retrieves a dictionary of properties for a path.
        
        @type   path:   string
        @param  path:   A file or directory path.
        
        @rtype:         dictionary
        @return:        A dictionary of properties.
        
        """
        
        return self.client.proplist(path)[0][1]
        
    def propget(self, path, prop_name):
        """
        Retrieves a dictionary of the prop_value of the given
        path and prop_name
        
        @type   path:       string
        @param  path:       A file or directory path.
        
        @type   prop_name:  string or self.PROPERTIES
        @param  prop_name:  An svn property name.
        
        @rtype:             dictionary
        @return:            A dictionary where the key is the path, the value 
                            is the prop_value.
        
        """

        path = self.proppath(path)
        
        try:
            returner = self.client.propget(
                prop_name,
                path,
                recurse=True
            )
        except pysvn.ClientError, e:
            print "pysvn.ClientError exception in svn.py propget()"
            print str(e)
            return ""
        
        try:
            returner = returner[path]
        except KeyError, e:
            returner = ""
            
        return returner
        
    def propdel(self, path, prop_name):
        """
        Removes a property from a given path
        
        @type   path: string
        @param  path: A file or directory path.
        
        @type   prop_name: string or self.PROPERTIES
        @param  prop_name: An svn property name.
        
        """
        
        path = self.proppath(path)
        
        returner = False
        try:
            self.client.propdel(
                prop_name,
                path,
                recurse=True
            )
            returner = True
        except pysvn.ClientError, e:
            print "pysvn.ClientError exception in svn.py propdel()"
            print str(e)
        except TypeError, e:
            print "TypeError exception in svn.py propdel()"
            print str(e)
        
        return returner
    
    #
    # callbacks
    #
    
    def set_callback_cancel(self, func):
        self.client.callback_cancel = func
    
    def callback_cancel(self):
        if hasattr(self.client, "callback_cancel"):
            self.client.callback_cancel()

    def set_callback_notify(self, func):
        self.client.callback_notify = func
    
    def set_callback_get_log_message(self, func):
        self.client.callback_get_log_message = func
        
    def set_callback_get_login(self, func):
        self.client.callback_get_login = func
    
    def set_callback_ssl_server_trust_prompt(self, func):
        self.client.callback_ssl_server_trust_prompt = func
    
    def set_callback_ssl_client_cert_password_prompt(self, func):
        self.client.callback_ssl_client_cert_password_prompt = func
    
    #
    # revision
    #
    
    def revision(self, kind, date=None, number=None):
        """
        Create a revision object usable by pysvn
        
        @type   kind:   string
        @param  kind:   An svn.REVISIONS keyword.
        
        @type   date:   integer
        @param  date:   Used for kind=date, in the form of UNIX TIMESTAMP (secs).
        
        @type   number: integer
        @param  number: Used for kind=number, specifies the revision number.
        
        @rtype:         pysvn.Revision object
        @return:        A pysvn.Revision object.
        
        """
        
        try:
            pysvn_obj = self.REVISIONS[kind]
        except KeyError, e:
            print "pysvn.ClientError exception in svn.py revision()"
            print str(e)
            return None
        
        returner = None
        if kind == "date":
            if date is None:
                print "In svn.py revision(),kind = date, but date not given"
                return None
            
            returner = pysvn.Revision(pysvn_obj, date)
        
        elif kind == "number":
            if number is None:
                print "In svn.py revision(),kind = number, but number not given"
                return None
        
            returner = pysvn.Revision(pysvn_obj, number)
        
        else:
            returner = pysvn.Revision(pysvn_obj)
        
        return returner
        
    #
    # actions
    #
    
    def add(self, *args, **kwargs):
        """
        Add files or directories to the repository
        
        @type   paths: list
        @param  paths: A list of files/directories.
        
        """
        
        return self.action(self.client.add, *args, **kwargs)
    
    def copy(self, *args, **kwargs):
        """
        Copy files/directories from src to dest.  src or dest may both be either
        a local path or a repository URL.  revision is a pysvn.Revision object.
        
        @type   src: string
        @param  src: Source URL or path.
        
        @type   dest: string
        @param  dest: Destination URL or path.
        
        @type   revision: pysvn.Revision object
        @param  revision: A pysvn.Revision object.
        
        """

        return self.action(self.client.copy, *args, **kwargs)
    
    def checkout(self, *args, **kwargs):
        
        """
        Checkout a working copy from a vcs repository
        
        @type   url: string
        @param  url: A repository url.
        
        @type   path: string
        @param  path: A local destination for the working copy.
        
        @type   recurse: boolean
        @param  recurse: Whether or not to run a recursive checkout.
        
        @type   ignore_externals: boolean
        @param  ignore_externals: Whether or not to ignore externals.
        
        """
        
        return self.action(self.client.checkout, *args, **kwargs)
    
    def cleanup(self, *args, **kwargs):
        """
        Clean up a working copy.
        
        @type   path: string
        @param  path: A local working copy path.
        
        """
        
        return self.action(self.client.cleanup, *args, **kwargs)
        
    def revert(self, *args, **kwargs):
        """
        Revert files or directories so they are unversioned
        
        @type   paths: list
        @param  paths: A list of files/directories.
        
        """
        
        return self.action(self.client.revert, *args, **kwargs)

    def commit(self, *args, **kwargs):
        """
        Commit a list of files to the repository.
        
        @type   paths: list
        @param  paths: A list of files/directories.
        
        @type   log_message: string
        @param  log_message: A commit log message.
        
        @type   recurse: boolean
        @param  recurse: Whether or not to recurse into sub-directories.
        
        @type   keep_locks: boolean
        @param  keep_locks: Whether or not to keep locks on commit.
        
        """
        
        return self.action(self.client.checkin, *args, **kwargs)
    
    def action(self, func, *args, **kwargs):
        """
        Perform a vcs action.
        
        @type   func: def
        @param  func: A function.
        
        """
        
        try:
            func(*args, **kwargs)
        except pysvn.ClientError, e:
            return str(e)
        except TypeError, e:
            return str(e)
        
        return None

class StatusMonitor():
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
    
    #: TODO: this is the reverse of C{STATUS} in the svn module and should probably
    #: be moved there once I figure out what the responsibilities for the svn
    #: module are.
    STATUS = {
        pysvn.wc_status_kind.none:          "none",
        pysvn.wc_status_kind.unversioned:   "unversioned",
        pysvn.wc_status_kind.normal:        "normal",
        pysvn.wc_status_kind.added:         "added",
        pysvn.wc_status_kind.missing:       "missing",
        pysvn.wc_status_kind.deleted:       "deleted",
        pysvn.wc_status_kind.replaced:      "replaced",
        pysvn.wc_status_kind.modified:      "modified",
        pysvn.wc_status_kind.merged:        "merged",
        pysvn.wc_status_kind.conflicted:    "conflicted",
        pysvn.wc_status_kind.ignored:       "ignored",
        pysvn.wc_status_kind.obstructed:    "obstructed",
        pysvn.wc_status_kind.external:      "external",
        pysvn.wc_status_kind.incomplete:    "incomplete"
    }
    
   
    #: A dictionary to keep track of the paths we're watching.
    #: 
    #: It looks like:::
    #:
    #:     watches = {
    #:         # Always None because we just want to check if a watch has been set
    #:         "/foo/bar/baz": None
    #:     }
    #:     
    watches = {}
    
    #: The mask for the inotify events we're interested in.
    #: TODO: understand how masking works
    #: TODO: maybe we should just analyze VCSProcessEvent and determine this 
    #: dynamically because one might tend to forgot to update these
    mask = EventsCodes.IN_MODIFY | EventsCodes.IN_MOVED_TO
    
    class VCSProcessEvent(ProcessEvent):
        """
        
        Our processing class for inotify events.
        
        """
        
        def __init__(self, status_monitor):
            self.status_monitor = status_monitor
        
        def process(self, event):
            path = event.path
            if event.name: path = os.path.join(path, event.name)
            
            # Begin debugging code
            print "Debug: Event %s triggered for: %s" % (event.event_name, path.rstrip(os.path.sep))
            # End debugging code
            
            # Make sure to strip any trailing slashes because that will 
            # cause problems for the status checking
            # TODO: not 100% sure about it causing problems
            self.status_monitor.status(path.rstrip(os.path.sep), invalidate=True)
    
        def process_IN_MODIFY(self, event):
            self.process(event)
        
        def process_IN_MOVED_TO(self, event):
            # FIXME: because update_file_info isn't called when things are moved,
            # and we can't convert a path/uri to a NautilusVFSFile we can't
            # always update the emblems properly on items that are moved (our 
            # nautilusVFSFile_table points to an item that no longer exists).
            #
            # Once get_file_items() is called on an item, we once again have the 
            # NautilusVFSFile we need (happens whenever an item is selected).
            self.process(event)
    
    def __init__(self, callback):
        self.callback = callback
        
        self.vcs_client = SVN()
        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(
            self.watch_manager, self.VCSProcessEvent(self))
        self.notifier.start()
    
    @timeit
    def add_watch(self, path):
        """
        
        Request a watch to be added for path. This function will figure out
        the best spot to add the watch (most likely a parent directory).
        
        TODO: refactor to remove code duplication
        MARKER: performance 
        
        """
        
        if not path in self.watches:
            # We can safely ignore items that aren't inside a working_copy or
            # a working copy administration area (.svn)
            if (path.find(".svn") > 0 or 
                    self.vcs_client.is_in_a_or_a_working_copy(path)):
                self.watches[path] = None
                # TODO: figure out precisely how this watch is added. Does it:
                #
                #  - Recursively register watches
                #  - Call the process method with the path argument originally used
                #    or with the path for the specific item that was modified.
                # 
                # FIXME: figure out why when registering a parent directory and the 
                # file itself the IN_MODIFY event handler is called 3 times (once 
                # for the directory and twice for the file itself).
                #
                
                # We only have to add a full recursive watch once, then we just
                # add new watches dynamically when events are triggered. So look
                # up to see whether there's already a watch set.
                
                # MARKER: performance 
                path_to_check = path
                watch_is_already_set = False
                while path_to_check !="":
                    path_to_check = split_path(path_to_check)
                    if path_to_check in self.watches:
                        watch_is_already_set = True
                        break;
                
                # To always be able to track moves (renames are moves too) we 
                # have to make sure we register with our parent directory
                if not watch_is_already_set:
                    parent_path = split_path(path)
                    
                    if (parent_path.find(".svn") > 0 or 
                            self.vcs_client.is_in_a_or_a_working_copy(parent_path)):
                        path_to_be_watched = parent_path
                    else:
                        path_to_be_watched = path
                    
                    self.watches[path_to_be_watched] = None # don't need a value
                    self.watch_manager.add_watch(path_to_be_watched, self.mask, rec=True)
                    # Begin debugging code
                    print "Debug: StatusMonitor.add_watch() added watch for %s" % path_to_be_watched
                    # End debugging code
                
                # Note that we don't have to set invalidate to True here to 
                # bypass the cache because since there isn't one it will be
                # bypassed anyways. We could add it for clarity though.
                # Begin debugging code
                print "Debug: StatusMonitor.add_watch() initial status check for %s" % path
                # End debugging code
                self.status(path)
        
    def status(self, path, invalidate=False):
        """
        
        This function doesn't return anything but calls the callback supplied
        to C{StatusMonitor} by the caller.
        
        UML sequence diagram depicting the status checks::
        
            +-----------------+                  +-------------+
            |  StatusMonitor  |                  |  VCSClient  |
            +-----------------+                  +-------------+
                    |                                   |
                    |    status(path, depth=empty)      |
                    |---------------------------------->|
                    |+-------------------+-------------+|
                    || [if isdir(path)]  |             ||
                    |+-------------------+             ||
                    ||                                 ||
                    ||          status(path)           ||
                    ||-------------------------------->||
                    |+---------------------------------+|
                    |                                   |
                    |+--------------------------+------+|
                    || [foreach parent folder]  |      ||
                    |+--------------------------+      ||
                    ||                                 ||
                    ||          status(path)           ||
                    ||-------------------------------->||
                    |+---------------------------------+|
                    |                                   |
        
        @type   path: string
        @param  path: The path for which to check the status.
        
        @type   invalidate: boolean
        @param  invalidate: Whether or not the cache should be bypassed.
        """
        
        # If we're not a or inside a working copy we don't even have to bother.
        if not self.vcs_client.is_in_a_or_a_working_copy(path): return
            
        # Subversion (pysvn? svn?) makes temporary files for some purpose which
        # are detected by inotify but are deleted shortly thereafter. So we
        # ignore them.
        # TODO: this obviously doesn't account for the fact that people might
        # version files with a .tmp extension.
        if path.endswith(".tmp"): return
        
        # Begin debugging information
        print "Debug: StatusMonitor.status() called for %s with %s" % (path, invalidate)
        # End debugging information
        
        # We need the status object for the item alone
        # MARKER: performance 
        status = self.vcs_client.status_with_cache(
            path, 
            invalidate=invalidate, 
            depth=pysvn.depth.empty)[-1].data["text_status"]
            
        # A directory should have a modified status when any of its children
        # have a certain status (see modified_statuses below). Jason thought up 
        # of a nifty way to do this by using sets and the bitwise AND operator (&).
        if isdir(path) and status != pysvn.wc_status_kind.added:
            modified_statuses = set([
                pysvn.wc_status_kind.added, 
                pysvn.wc_status_kind.deleted, 
                pysvn.wc_status_kind.modified
            ])
            
            # MARKER: performance 
            sub_statuses = self.vcs_client.status_with_cache(path, invalidate=invalidate)[:-1]
            statuses = set([sub_status.data["text_status"] for sub_status in sub_statuses])
            
            if len(modified_statuses & statuses): 
                self.callback(path, "modified")
                
                #
                # We have to change the emblems on any parent directories aswell
                # when an item is modified this is pretty easy because we know
                # the status for the parent has to be "modified" too.
                #
                # There's another section below which also takes into account
                # the other statuses.
                #
                while path != "":
                    path = split_path(path)
                    if self.vcs_client.is_in_a_or_a_working_copy(path):
                        self.callback(path, "modified")
                        break;
                return;
        
        # Verifiying the rest of the statuses is common for both files and directories.
        if status in self.STATUS:
            self.callback(path, self.STATUS[status])
            
            # Now we have to invalidate the parent directories
            while path != "":
                path = split_path(path)
                if not self.vcs_client.is_in_a_or_a_working_copy(path): return
                    
                if status in (
                    pysvn.wc_status_kind.added, 
                    pysvn.wc_status_kind.deleted, 
                    pysvn.wc_status_kind.modified,
                ):
                    # FIXME: we should probably bypass the cache here
                    if not self.vcs_client.is_added(path):
                        self.callback(path, "modified")
                elif status in (
                        pysvn.wc_status_kind.normal,
                        pysvn.wc_status_kind.unversioned, # FIXME: but only if it was previously versioned
                    ):
                    
                    # MARKER: performance 
                    self.status(path, invalidate=invalidate)
                    
                    # If we don't break out here it would result in the 
                    # recursive status checks on (^):
                    #
                    # /foo/bar/baz/qux
                    #   ^   ^   ^
                    #   ^   ^
                    #   ^
                    #
                    # Instead of "just":
                    #
                    # /foo/bar/baz/qux
                    #   ^   ^   ^
                    #
                    
                    # FIXME: if those were just cache hits performance would
                    # be significantly increased.
                    break;
