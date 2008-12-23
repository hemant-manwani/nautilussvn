#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
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

import os.path
from os.path import isdir, isfile

import pysvn

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
        pysvn.wc_notify_action.update_add:              "Addd",
        pysvn.wc_notify_action.update_update:           "Updated",
        pysvn.wc_notify_action.update_completed:        "Completed",
        pysvn.wc_notify_action.update_external:         "External",
        pysvn.wc_notify_action.status_completed:        "Completed",
        pysvn.wc_notify_action.status_external:         "External",
        pysvn.wc_notify_action.commit_modified:         "Modified",
        pysvn.wc_notify_action.commit_added:            "Added",
        pysvn.wc_notify_action.commit_deleted:          "Copied",
        pysvn.wc_notify_action.commit_replaced:         "Replaced",
        pysvn.wc_notify_action.commit_postfix_txdelta:  "Postfix Delta",
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
    
    def __init__(self):
        self.client = pysvn.Client()
    
    #
    # is
    #
    
    def is_working_copy(self, path):
        if (isdir(path) and
                isdir(os.path.join(path, ".svn"))):
            return True
        
        return False
        
    def is_in_a_or_a_working_copy(self, path):
        # If we're a file we have to check the directory we're in instead
        if isfile(path):
            path = os.path.abspath(os.path.join(path, os.path.pardir))
        
        if self.is_working_copy(path):
            return True
            
        return False
        
    def is_versioned(self, path):
        
        # info will return nothing for an unversioned file inside a working copy
        if self.client.info(path):
            return True
        
        return False
    
    def is_normal(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.normal:
            return True
        
        return False
    
    def is_added(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.added:
            return True
        
        return False
        
    def is_modified(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.modified:
            return True
        
        return False
    
    def is_deleted(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.deleted:
            return True
        
        return False
        
    def is_ignored(self, path):
        all_status = self.client.status(path)
        status = all_status[len(all_status) - 1]
        
        if status.data["text_status"] == pysvn.wc_status_kind.ignored:
            return True
        
        return False
        
        
    #
    # has
    #
    
    def has_unversioned(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.unversioned:
                return True
                
        return False
    
    def has_added(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.added:
                return True
                
        return False
        
    def has_modified(self, path):
        all_status = self.client.status(path)[:-1]
        
        for status in all_status:
            if status.data["text_status"] == pysvn.wc_status_kind.modified:
                return True
        
        return False

    def has_deleted(self, path):
        all_status = self.client.status(path)[:-1]
        
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
        
        @type   paths: list
        @param  paths: a list of paths or files
        
        @type   statuses: list
        @param  statuses: a list of pysvn.wc_status_kind statuses
        
        @rtype list
        @returner a list of PysvnStatus objects
        
        """

        if paths is None:
            return []
 
        #recursively searches the common path of all "paths" item
        st = self.client.status(
            os.path.commonprefix(paths)[len(os.getcwd())+1:]
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
        
        @type   path: string
        @param  path: a working copy path
        
        @rtype  string
        @return a repository URL
        
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
        
        @type   path: string
        @param  path: a working copy path
        
        @rtype  int
        @return a repository revision
        
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

        @type   path: string
        @param  path: a file or directory path
        
        @rtype  string
        @return a prop* function-safe path

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
        @param  path: a file or directory path
        
        @type   prop_name: string
        @param  prop_name: an svn property name
        
        @type   prop_value: string
        @param  prop_value: an svn property value/pattern
        
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
        Retrieves a dict of properties for a path
        
        @type   path: string
        @param  path: a file or directory path
        
        @rtype  dict
        @return a dict of properties
        
        """
        
        return self.client.proplist(path)[0][1]
        
    def propget(self, path, prop_name):
        """
        Retrieves a dictionary of the prop_value of the given
        path and prop_name
        
        @type   path: string
        @param  path: a file or directory path
        
        @type   prop_name: string or self.PROPERTIES
        @param  prop_name: an svn property name
        
        @rtype  dict
        @return a dict where the key is the path, the value is the prop_value
        
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
        @param  path: a file or directory path
        
        @type   prop_name: string or self.PROPERTIES
        @param  prop_name: an svn property name
        
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
    # actions
    #
    
    def add(self, paths):
        """
        Add files or directories to the repository
        
        @type   paths: list
        @param  paths: a list of files/directories
        
        """
        
        if paths is None:
            return

        try:
            self.client.add(paths)
        except pysvn.ClientError, e:
            print "pysvn.ClientError exception in svn.py add()"
            print str(e)
        except TypeError, e:
            print "TypeError exception in svn.py add()"
            print str(e)
