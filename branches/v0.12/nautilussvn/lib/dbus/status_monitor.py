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

import gobject

import dbus
import dbus.glib
import dbus.service
import dbus.mainloop.glib

from nautilussvn.lib.vcs.svn import StatusMonitor as SVNStatusMonitor

INTERFACE = "org.google.code.nautilussvn.StatusMonitor"
OBJECT_PATH = "/org/google/code/nautilussvn/StatusMonitor"
SERVICE = "org.google.code.nautilussvn.NautilusSvn"

class StatusMonitor(dbus.service.Object):
    
    def __init__(self, connection):
        dbus.service.Object.__init__(self, connection, OBJECT_PATH)
        self.status_monitor = SVNStatusMonitor(self.StatusChanged)
        
    @dbus.service.signal(INTERFACE)
    def StatusChanged(self, path, status):
        pass
    
    @dbus.service.method(INTERFACE)
    def change_status(self, path, status):
        self.StatusChanged(path, status)
        
    @dbus.service.method(INTERFACE)
    def has_watch(self, path):
        # FIXME: still doesn't return an actual boolean but 1/0.
        return bool(self.status_monitor.has_watch(str(path)))
        
    @dbus.service.method(INTERFACE)
    def add_watch(self, path):
        self.status_monitor.add_watch(str(path))
        
    @dbus.service.method(INTERFACE)
    def status(self, path, invalidate=False):
        # FIXME: this will eventually call StatusChanged even though the
        # status might not have been changed at all. This is fine right now
        # because only the Nautilus extension is using the DBus service but
        # wouldn't be if other people started using it to stay up to date 
        # about VCS events.
        self.status_monitor.status(str(path), bool(invalidate))
        
    @dbus.service.method(INTERFACE, in_signature="", out_signature="")
    def exit(self):
        self.status_monitor.notifier.stop()
        loop.quit()
        
class StatusMonitorStub:
    
    def __init__(self, callback):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        
        self.callback = callback
        self.bus = dbus.SessionBus()
        
        try:
            self.object = self.bus.get_object(SERVICE, OBJECT_PATH)
            self.object.connect_to_signal("StatusChanged", self.cb_status, dbus_interface=INTERFACE)
        except dbus.DBusException:
            traceback.print_exc()
    
    def has_watch(self, path):
        return self.object.has_watch(path, dbus_interface=INTERFACE)
        
    def add_watch(self, path):
        self.object.add_watch(path, dbus_interface=INTERFACE)
    
    def status(self, path, invalidate=False):
        self.object.status(path, invalidate, dbus_interface=INTERFACE)
    
    def cb_status(self, path, status):
        self.callback(str(path), str(status))
        
if __name__ == "__main__":
    gobject.threads_init()
    dbus.glib.threads_init()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(SERVICE, session_bus)
    status_monitor = StatusMonitor(session_bus)
    
    loop = gobject.MainLoop()
    loop.run()
