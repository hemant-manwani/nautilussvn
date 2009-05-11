import traceback
import thread

import dbus
import dbus.service

from nautilussvn.statusmonitor import StatusMonitor as RealStatusMonitor

INTERFACE = "org.google.code.nautilussvn.StatusMonitor"
OBJECT_PATH = "/org/google/code/nautilussvn/StatusMonitor"
SERVICE = "org.google.code.nautilussvn.NautilusSvn"

class StatusMonitor(dbus.service.Object):
    
    def __init__(self, connection):
        dbus.service.Object.__init__(self, connection, OBJECT_PATH)
            
        self.status_monitor = RealStatusMonitor(self.WatchAdded, self.StatusChanged)
        
    @dbus.service.signal(INTERFACE)
    def StatusChanged(self, path, status):
        pass
    
    @dbus.service.signal(INTERFACE)
    def WatchAdded(self, path):
        pass
    
    @dbus.service.method(INTERFACE)
    def ChangeStatus(self, path, status):
        self.StatusChanged(path, status)
        
    @dbus.service.method(INTERFACE)
    def HasWatch(self, path):
        return self.status_monitor.has_watch(path)
        
    @dbus.service.method(INTERFACE)
    def AddWatch(self, path):
        self.status_monitor.add_watch(path)
        
    @dbus.service.method(INTERFACE)
    def Status(self, path, invalidate=False, recursive=True):
        self.status_monitor.status(path, invalidate=invalidate, recursive=recursive)
        
class StatusMonitorStub:
    """
    This isn't something from DBus but it looked like a good idea to me to
    make using the StatusMonitor easier. We can probably do this dynamically
    though, maybe request an object path and then get a generated stub back.
    """
    
    def __init__(self, status_callback, watch_callback):
        self.session_bus = dbus.SessionBus()
        
        self.status_callback = status_callback
        self.watch_callback = watch_callback
        
        try:
            self.status_monitor = self.session_bus.get_object(SERVICE, OBJECT_PATH)
            self.status_monitor.connect_to_signal("StatusChanged", self.cb_status, dbus_interface=INTERFACE)
            self.status_monitor.connect_to_signal("WatchAdded", self.cb_watch_added, dbus_interface=INTERFACE)
        except dbus.DBusException:
            traceback.print_exc()
    
    def has_watch(self, path):
        return bool(self.status_monitor.HasWatch(path, dbus_interface=INTERFACE))
        
    def add_watch(self, path):
        self.status_monitor.AddWatch(
            path, 
            dbus_interface=INTERFACE,
            reply_handler=lambda: True,
            error_handler=lambda e: True
        )
    
    def status(self, path, invalidate=False, recursive=True):
        self.status_monitor.Status(
            path, 
            invalidate, 
            recursive,
            dbus_interface=INTERFACE,
            reply_handler=lambda: True,
            error_handler=lambda e: True
        )
    
    def cb_status(self, path, status):
        self.status_callback(path, status)
        
    def cb_watch_added(self, path):
        self.watch_callback(path)
