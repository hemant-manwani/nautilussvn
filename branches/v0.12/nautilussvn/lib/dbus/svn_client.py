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

import traceback

import dbus
import dbus.service

from nautilussvn.lib.vcs.svn import SVN, PySVN

INTERFACE = "org.google.code.nautilussvn.SVNClient"
OBJECT_PATH = "/org/google/code/nautilussvn/SVNClient"
SERVICE = "org.google.code.nautilussvn.NautilusSvn"

class SVNClient(dbus.service.Object):
    """
    FIXME: this is only a temporary hack to have all functionality in the
    extension use the status cache. It _will_ be refactored.
    """
    
    def __init__(self, connection):
        dbus.service.Object.__init__(self, connection, OBJECT_PATH)            

        self.pysvn = PySVN()
        self.svn_client = SVN()
    
    @dbus.service.method(INTERFACE)
    def StatusWithCache(self, path, invalidate=False):
        return self.pysvn.convert_pysvn_statuses(
            self.svn_client.status_with_cache(str(path), bool(invalidate)))
    
    @dbus.service.method(INTERFACE)
    def IsWorkingCopy(self, path):
        return self.svn_client.is_working_copy(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsInAOrAWorkingCopy(self, path):
        return self.svn_client.is_in_a_or_a_working_copy(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsVersioned(self, path):
        return self.svn_client.is_versioned(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsNormal(self, path):
        return self.svn_client.is_normal(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsAdded(self, path):
        return self.svn_client.is_added(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsModified(self, path):
        return self.svn_client.is_modified(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsDeleted(self, path):
        return self.svn_client.is_deleted(str(path))
    
    @dbus.service.method(INTERFACE)
    def IsIgnored(self, path):
        return self.svn_client.is_ignored(str(path))

    @dbus.service.method(INTERFACE)
    def IsLocked(self, path):
        return self.svn_client.is_locked(str(path))

    @dbus.service.method(INTERFACE)
    def IsConflicted(self, path):
        return self.svn_client.is_conflicted(str(path))
    
    @dbus.service.method(INTERFACE)
    def HasUnversioned(self, path):
        return self.svn_client.has_unversioned(str(path))
    
    @dbus.service.method(INTERFACE)
    def HasAdded(self, path):
        return self.svn_client.has_added(str(path))
    
    @dbus.service.method(INTERFACE)
    def HasModified(self, path):
        return self.svn_client.has_modified(str(path))
    
    @dbus.service.method(INTERFACE)
    def HasDeleted(self, path):
        return self.svn_client.has_deleted(str(path))

    @dbus.service.method(INTERFACE)
    def HasIgnored(self, path):
        return self.svn_client.has_ignored(str(path))

    @dbus.service.method(INTERFACE)
    def HasLocked(self, path):
        return self.svn_client.has_locked(str(path))

    @dbus.service.method(INTERFACE)
    def HasConflicted(self, path):
        return self.svn_client.has_conflicted(str(path))
    
    @dbus.service.method(INTERFACE, in_signature="", out_signature="")
    def Exit(self):
        pass
        
class SVNClientStub:
    
    def __init__(self):
        self.session_bus = dbus.SessionBus()
        
        try:
            self.svn_client = self.session_bus.get_object(SERVICE, OBJECT_PATH)
        except dbus.DBusException:
            traceback.print_exc()
    
    def status_with_cache(self, path, invalidate=False):
        return self.svn_client.StatusWithCache(path, invalidate)
    
    def is_working_copy(self, path):
        return self.svn_client.IsWorkingCopy(path)
    
    def is_in_a_or_a_working_copy(self, path):
        return self.svn_client.IsInAOrAWorkingCopy(path)
    
    def is_versioned(self, path):
        return self.svn_client.IsVersioned(path)
    
    def is_normal(self, path):
        return self.svn_client.IsNormal(path)
    
    def is_added(self, path):
        return self.svn_client.IsAdded(path)
    
    def is_modified(self, path):
        return self.svn_client.IsModified(path)
    
    def is_deleted(self, path):
        return self.svn_client.IsDeleted(path)
    
    def is_ignored(self, path):
        return self.svn_client.IsIgnored(path)

    def is_locked(self, path):
        return self.svn_client.IsLocked(path)

    def is_conflicted(self, path):
        return self.svn_client.IsConflicted(path)
    
    def has_unversioned(self, path):
        return self.svn_client.HasUnversioned(path)
    
    def has_added(self, path):
        return self.svn_client.HasAdded(path)
    
    def has_modified(self, path):
        return self.svn_client.HasModified(path)
    
    def has_deleted(self, path):
        return self.svn_client.HasDeleted(path)

    def has_ignored(self, path):
        return self.svn_client.HasIgnored(path)

    def has_locked(self, path):
        return self.svn_client.HasLocked(path)

    def has_conflicted(self, path):
        return self.svn_client.HasConflicted(path)
    
    def exit(self):
        self.svn_client.Exit()
