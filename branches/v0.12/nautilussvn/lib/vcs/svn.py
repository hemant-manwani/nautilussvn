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
    """
    
    """
    
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
        STATUS["missing"]
    ]

    STATUSES_FOR_REVERT = [
        STATUS["missing"],
        STATUS["added"],
        STATUS["modified"]
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
    #: It might look like:::
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
        This function will eventually be deprecated for status_with_cache.
        
        """
        if depth:
            return self.client.status(path, depth=depth)
        else:
            return self.client.status(path, recurse=recurse)
    
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
        try:
            if (invalidate or 
                    path not in self.status_cache or
                    # The following condition is used to bypass the cache when
                    # an infinity check is requesting and it's most likely
                    # that only an empty check was done before.
                    (depth == pysvn.depth.infinity and
                        len(self.status_cache[path]) == 1)):
                #~ print "Debug: status_with_cache() invalidated %s" % path
                statuses = self.client.status(path, depth=depth)
            else:
                return self.status_cache[path]
        except pysvn.ClientError:
            statuses = [pysvn.PysvnStatus({"text_status": pysvn.wc_status_kind.none})]
        
        # If we do end up here the cache was bypassed.
        self.status_cache[path] = statuses
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
    
    def is_locked(self, path):
        is_locked = False
        try:
            is_locked = self.client.info2(path)[0][1].lock is not None
        except pysvn.ClientError, e:
            print str(e)
            
        return is_locked
    #
    # has
    #
    
    def has_unversioned(self, path):
        statuses = self.status_with_cache(path, depth=pysvn.depth.infinity)[:-1]
        
        for status in statuses:
            if status.data["text_status"] == pysvn.wc_status_kind.unversioned:
                return True
                
        return False
    
    def has_added(self, path):
        statuses = self.status_with_cache(path, depth=pysvn.depth.infinity)[:-1]
        
        for status in statuses:
            if status.data["text_status"] == pysvn.wc_status_kind.added:
                return True
                
        return False
        
    def has_modified(self, path):
        statuses = self.status_with_cache(path, depth=pysvn.depth.infinity)[:-1]
        
        for status in statuses:
            if status.data["text_status"] == pysvn.wc_status_kind.modified:
                return True
        
        return False

    def has_deleted(self, path):
        statuses = self.status_with_cache(path, depth=pysvn.depth.infinity)[:-1]
        
        for status in statuses:
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
            dirs = []
            for i in paths:
                dirs.append(os.path.dirname(i))
            path = os.path.commonprefix(dirs)
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

        if not self.is_versioned(path) and os.path.isfile(path):
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
        
        returner = self.client.proplist(path)
        if returner:
            returner = returner[0][1]
        else:
            returner = {}
            
        return returner
        
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
        
        @type   recurse: boolean
        @param  recurse: Recursively add a directory's children
        
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
    
    def log(self, *args, **kwargs):
        """
        Retrieve log items for a given path in the repository
        
        @type   url_or_path: string
        @param  url_or_path: Path for which to get log items for
        
        @type   revision_start: pysvn.Revision
        @param  revision_start: Most recent revision.  Defaults to HEAD
        
        @type   revision_end: pysvn.Revision
        @param  revision_end: Oldest revision.  Defaults to rev 0.
        
        @type   limit: int
        @param  limit: The maximum number of items to return.  Defaults to 0.
        
        """
        
        return self.action(self.client.log, *args, **kwargs)

    def export(self, *args, **kwargs):
        
        """
        Export files from either a working copy or repository into a local
        path without versioning information.
        
        @type   src_url_or_path: string
        @param  src_url_or_path: A repository url.
        
        @type   dest_path: string
        @param  dest_path: A local destination for the working copy.
        
        @type   revision: pysvn.Revision
        @param  revision: The revision to retrieve from the repository.
        
        @type   recurse: boolean
        @param  recurse: Whether or not to run a recursive checkout.
        
        @type   ignore_externals: boolean
        @param  ignore_externals: Whether or not to ignore externals.
        
        """
        
        return self.action(self.client.export, *args, **kwargs)

    def import_(self, *args, **kwargs):
        
        """
        Import an unversioned file or directory structure into a repository.
        
        @type   path: string
        @param  path: An unversioned file or directory structure
        
        @type   url: string
        @param  url: A repository location to put the imported files
        
        @type   log_message: string
        @param  log_message: Log message to use for commit
        
        @type   ignore: boolean
        @param  ignore: Disregard svn:ignore props
        
        """
        
        return self.action(self.client.import_, *args, **kwargs)

    def lock(self, *args, **kwargs):
        
        """
        Lock a url or path.
        
        @type   url_or_path: string
        @param  url_or_path: A url or path to lock
        
        @type   lock_comment: string
        @param  lock_comment: A log message to go along with the lock.

        @type   force: boolean
        @param  force: Steal the locks of others if they exist.
        
        """
        
        return self.action(self.client.lock, *args, **kwargs)

    def relocate(self, *args, **kwargs):
        
        """
        Relocate the working copy from from_url to to_url for path
        
        @type   from_url: string
        @param  from_url: A url to relocate from
        
        @type   to_url: string
        @param  to_url: A url to relocate to

        @type   path: string
        @param  path: The path of the local working copy
        
        """
        
        return self.action(self.client.relocate, *args, **kwargs)
        
    def move(self, *args, **kwargs):
        
        """
        Schedule a file to be moved around the repository
        
        @type   src_url_or_path: string
        @param  src_url_or_path: A url/path to move from
        
        @type   dest_url_or_path: string
        @param  dest_url_or_path: A url/path to move to

        @type   force: boolean
        @param  force: Force renaming, despite conflicts. Defaults to false.
        
        """
        
        return self.action(self.client.move, *args, **kwargs)

    def remove(self, *args, **kwargs):
        
        """
        Schedule a file to be removed from the repository
        
        @type   url_or_path: string
        @param  url_or_path: A url/path to remove

        @type   force: boolean
        @param  force: Force renaming, despite conflicts. Defaults to false.

        @type   keep_local: boolean
        @param  keep_local: Keep the local copy (don't just delete it)        
                
        """
        
        return self.action(self.client.remove, *args, **kwargs)

    def revert(self, *args, **kwargs):
        """
        Revert files or directories from the repository
        
        @type   paths: list
        @param  paths: A list of files/directories.
        
        @type   recurse: boolean
        @param  recurse: Recursively add a directory's children
        
        """
        
        return self.action(self.client.revert, *args, **kwargs)

    def resolve(self, *args, **kwargs):
        """
        Mark conflicted files as resolved
        
        @type   path: string
        @param  path: A local path to resolve
        
        @type   recurse: boolean
        @param  recurse: Recursively add a directory's children
        
        """
        
        return self.action(self.client.resolved, *args, **kwargs)

    def switch(self, *args, **kwargs):
        """
        Switch the working copy to another repository source.
        
        @type   path: string
        @param  path: A local path to a working copy
        
        @type   url: string
        @param  url: The repository location to switch to
        
        @type   revision: pysvn.Revision
        @param  revision: The revision of the repository to switch to (Def:HEAD)
        
        """
        
        return self.action(self.client.switch, *args, **kwargs)

    def unlock(self, *args, **kwargs):
        """
        Unlock locked files.
        
        @type   path: string
        @param  path: A local path to resolve
        
        @type   force: boolean
        @param  force: If locked by another user, unlock it anyway.
        
        """
        
        return self.action(self.client.unlock, *args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Update a working copy.
        
        @type   path: string
        @param  path: A local path to update
        
        @type   recurse: boolean
        @param  recurse: Update child folders recursively
        
        @type   revision: pysvn.Revision
        @param  revision: Revision to update to (Def: HEAD)
        
        @type   ignore_externals: boolean
        @param  ignore_externals: Ignore external items
        
        """
        
        return self.action(self.client.update, *args, **kwargs)

    def annotate(self, *args, **kwargs):
        """
        Get the annotate results for the given file and revision range.
        
        @type   url_or_path: string
        @param  url_or_path: A url or local path
                
        @type   from_revision: pysvn.Revision
        @param  from_revision: Revision from (def: 1)
        
        @type   to_revision: pysvn.Revision
        @param  to_revision: Revision to (def: HEAD)
                
        """
        
        return self.action(self.client.annotate, *args, **kwargs)

    def merge_ranges(self, *args, **kwargs):
        """
        Merge a range of revisions.
        
        @type   sources: list
        @param  sources: A repository location (unsure)
        
        @type   ranges_to_merge: list of tuples
        @param  ranges_to_merge: A list of revision ranges to merge
        
        @type   peg_revision: pysvn.Revision
        @param  peg_revision: Indicates which revision in sources is valid.
        
        @type   target_wcpath: string
        @param  target_wcpath: Target working copy path
        
        @type   notice_ancestry: boolean
        @param  notice_ancestry: unsure
        
        @type   force: boolean
        @param  force: unsure
        
        @type   dry_run: boolean
        @param  dry_run: Do a test/dry run or not
        
        @type   record_only: boolean
        @param  record_only: unsure
        
        TODO: Will firm up the parameter documentation later
        
        """
        
        return self.action(self.client.merge_peg2, *args, **kwargs)

    def merge_trees(self, *args, **kwargs):
        """
        Merge two trees into one.

        @type   url_or_path1: string
        @param  url_or_path1: From WC/URL location

        @type   revision1: pysvn.Revision
        @param  revision1: Indicates the revision of the URL/Path

        @type   url_or_path2: string
        @param  url_or_path2: To WC/URL location

        @type   revision2: pysvn.Revision
        @param  revision2: Indicates the revision of the URL/Path
        
        @type   local_path: string
        @param  local_path: Target working copy path
        
        @type   force: boolean
        @param  force: unsure
        
        @type   recurse: boolean
        @param  recurse: Merge children recursively
        
        @type   record_only: boolean
        @param  record_only: unsure
        
        TODO: Will firm up the parameter documentation later
        
        """
        
        return self.action(self.client.merge, *args, **kwargs)

    def action(self, func, *args, **kwargs):
        """
        Perform a vcs action.
        
        @type   func: def
        @param  func: A function.
        
        """
        
        returner = None
        try:
            returner = func(*args, **kwargs)
        except pysvn.ClientError, e:
            return str(e)
        except TypeError, e:
            return str(e)
        
        return returner

class StatusMonitor():
    """
    
    The C{StatusMonitor} is basically a replacement for the currently limited 
    C{update_file_info} function. 
    
    What C{StatusMonitor} does:
    
      - When somebody adds a watch and if there's not already a watch for this 
        item it will add one.
    
      - Use inotify to keep track of modifications of any watched items
        (we actually only care about modifications not creations and deletions)
        
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
               |        status(path)        |
               |--------------------------->|
               |                            |
               |  cb_status(path, status)   |
               |<---------------------------|
               |                            |
               |---+                        |
               |   | set_emblem_by_status(path, status)
               |<--+                        |
               |                            |

    
    """
    
    #: A set of statuses which count as modified in TortoiseSVN emblem speak.
    MODIFIED_STATUSES = [
        pysvn.wc_status_kind.added,
        pysvn.wc_status_kind.deleted,
        pysvn.wc_status_kind.replaced,
        pysvn.wc_status_kind.modified
    ]
    
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
    
    #: 
    #:
    status_cache = {}
    
    #: The mask for the inotify events we're interested in.
    #: TODO: understand how masking works
    #: TODO: maybe we should just analyze VCSProcessEvent and determine this 
    #: dynamically because one might tend to forgot to update these
    mask = EventsCodes.IN_MODIFY | EventsCodes.IN_MOVED_TO | EventsCodes.IN_CREATE
    
    class VCSProcessEvent(ProcessEvent):
        """
        
        Our processing class for inotify events.
        
        """
        
        def __init__(self, status_monitor):
            self.status_monitor = status_monitor
        
        def process(self, event):
            path = event.path
            if event.name: path = os.path.join(path, event.name)
            
            # We're only interested in the entries file from the Subversion
            # working copy administration area (.svn) not locks, etc.
            if path.find(".svn") != -1 and not path.endswith(".svn/entries"): return
            
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
            
        def process_IN_CREATE(self, event):
            # FIXME: we shouldn't be attaching watches, auto_add should handle this
            self.process(event)
    
    def __init__(self, callback):
        self.callback = callback
        
        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(
            self.watch_manager, self.VCSProcessEvent(self))
        self.notifier.start()
    
    def has_watch(self, path):
        return (path in self.watches)
    
    def add_watch(self, path):
        """
        Request a watch to be added for path. This function will figure out
        the best spot to add the watch (most likely a parent directory).
        """
        
        vcs_client = SVN()

        path_to_check = path
        path_to_attach = None
        watch_is_already_set = False
        
        while path_to_check != "":
            # If in /foo/bar/baz
            #                 ^
            # baz is unversioned, this will stay allow us to attach a watch and
            # keep an eye on it (for when it is added).
            if vcs_client.is_in_a_or_a_working_copy(path_to_check):
                path_to_attach = path_to_check
            
            if path_to_check in self.watches:
                watch_is_already_set = True
                break;
                
            path_to_check = split_path(path_to_check)
        
        if not watch_is_already_set and path_to_attach:
            self.watch_manager.add_watch(path_to_attach, self.mask, rec=True, auto_add=True)
            self.watches[path_to_attach] = None # don't need a value
            #~ print "Debug: StatusMonitor.add_watch() added watch for %s" % path_to_attach
            
        # Make sure we also attach watches for the path itself
        if (not path in self.watches and
                vcs_client.is_in_a_or_a_working_copy(path)):
            self.watches[path] = None
        
    def status(self, path, invalidate=False):
        """
        
        TODO: This function is really quite unmaintainable.
        
        This function doesn't return anything but calls the callback supplied
        to C{StatusMonitor} by the caller.
        
        @type   path: string
        @param  path: The path for which to check the status.
        
        @type   invalidate: boolean
        @param  invalidate: Whether or not the cache should be bypassed.
        """
        
        vcs_client = SVN()
        
        # Handle changes to an entries file a little bit differently 
        # TODO: if we could find out what was changed in the entries file that
        # would probably help
        if path.endswith(".svn/entries"):
            path = path[0:path.find(".svn")].rstrip("/")
            for item_basename in os.listdir(path):
                item_path = os.path.join(path, item_basename)
                self.status(item_path, invalidate=invalidate)
            return
            
        # Directories and all other files
        priority_status = None 
        while path != "":
            #~ print "Debug: StatusMonitor.status() called for %s with %s" % (path, invalidate)
            # Some statuses take precedence in relation to other statuses
            if priority_status == "conflicted":
                self.do_callback(path, "conflicted")
            else:
                try:
                    status = vcs_client.status_with_cache(
                        path, 
                        invalidate=invalidate, 
                        depth=pysvn.depth.empty)[-1].data["text_status"]
                except IndexError, e:
                    # TODO: This probably has to do with temporary files
                    print "    DEBUG: EXCEPTION in StatusMonitor.status(): %s" % str(e)
                    path = split_path(path)
                    continue
                    
                # Do a quick callback and then figure out the actual status
                self.do_callback(path, PySVN.STATUS[status])
                
                if isfile(path):
                    if status == SVN.STATUS["conflicted"]:
                        priority_status = "conflicted"
                        self.do_callback(path, "conflicted")
                    else:
                        if status in self.MODIFIED_STATUSES:
                            self.do_callback(path, PySVN.STATUS[status])
                elif isdir(path):
                    sub_statuses = vcs_client.status_with_cache(path, invalidate=invalidate)[:-1]
                    statuses = set([sub_status.data["text_status"] for sub_status in sub_statuses])
                    
                    # Let's figure out if we have any priority statuses
                    if SVN.STATUS["conflicted"] in statuses:
                        priority_status = "conflicted"
                        self.do_callback(path, "conflicted")
                    # No priority status, let's find out what we do have
                    else:
                        # An item it's own modified status takes precedence over the statuses of children.
                        if status in self.MODIFIED_STATUSES:
                            self.do_callback(path, PySVN.STATUS[status])
                        else:
                            # A directory should have a modified status when any of its children
                            # have a certain status (see modified_statuses below). Jason thought up 
                            # of a nifty way to do this by using sets and the bitwise AND operator (&).
                            if len(set(self.MODIFIED_STATUSES) & statuses):
                                self.do_callback(path, "modified")
                                
            path = split_path(path)
            
    def do_callback(self, path, status):
        """
        Figure out whether or not we should do a callback (if we do too many
        callbacks the extension will hang).
        """
        
        if path not in self.status_cache: 
            self.status_cache[path] = {
                "current_status": None,
                "previous_status": None
            }
            
        self.status_cache[path]["previous_status"] = self.status_cache[path]["current_status"]
        self.status_cache[path]["current_status"] = status
        
        if self.status_cache[path]["current_status"] != self.status_cache[path]["previous_status"]:
            self.callback(path, status)
        
class PySVN():
    """
    Used to convert all sorts of PySVN objects to primitives which can be 
    submitted over the DBus.
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
    
    REVISIONS = {
        pysvn.opt_revision_kind.unspecified:    "unspecified",
        pysvn.opt_revision_kind.number:         "number",
        pysvn.opt_revision_kind.date:           "date",
        pysvn.opt_revision_kind.committed:      "committed",
        pysvn.opt_revision_kind.previous:       "previous",
        pysvn.opt_revision_kind.working:        "working",
        pysvn.opt_revision_kind.head:           "head"
    }
    
    DEPTHS = {
        pysvn.depth.empty:      "empty",
        pysvn.depth.exclude:    "exclude",
        pysvn.depth.files:      "files",
        pysvn.depth.immediates: "immediates",
        pysvn.depth.infinity:   "infinity",
        pysvn.depth.unknown:    "unknown"
    }
    
    def convert_pysvn_statuses(self, pysvn_statuses):
        """
        Converts a list of C{PysvnStatus}es to a dictionary:::
            
            {
                "data": {
                    "text_status": "normal"
                    ...
                }
            }
            
        Sorta...
        
        """
        
        statuses = []
        
        for pysvn_status in pysvn_statuses:
            data = []
            for key, value in pysvn_status.data.items():
                try:
                    if value == None:
                        continue
                    elif isinstance(value, (str, int, unicode)):
                        data.append((key, value))
                    elif value in self.STATUS:
                        data.append((key, self.STATUS[value]))
                    
                except TypeError, e:
                    if str(e) == "unhashable instance":
                        continue
                    else:
                        raise e
                    
            statuses.append({
                "data": dict(data)
            })
            
        return statuses
