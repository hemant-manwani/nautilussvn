"""

This is our DBus service which registers all the objects we expose with the 
sesion bus.

"""

import os.path
import traceback
import subprocess
import time

import gobject

import dbus
import dbus.glib
import dbus.mainloop.glib
import dbus.service

from nautilussvn.dbus.status_monitor import StatusMonitor

INTERFACE = "org.google.code.nautilussvn.Service"
OBJECT_PATH = "/org/google/code/nautilussvn/Service"
SERVICE = "org.google.code.nautilussvn.NautilusSvn"

class Service(dbus.service.Object):
    
    def __init__(self, connection):
        dbus.service.Object.__init__(self, connection, OBJECT_PATH)
        
        # Register our objects with the session bus by instantiating them
        self.status_monitor = StatusMonitor(connection)
    
    @dbus.service.method(INTERFACE, in_signature="", out_signature="")
    def Exit(self):
        self.status_monitor.Exit()
        loop.quit()

def start():
    """
    This function is used to start our service.
    
    @rtype: boolean
    @return: Whether or not the service was successfully started.
    """
    try:
        session_bus = dbus.SessionBus()
        session_bus.get_object(SERVICE, OBJECT_PATH)
        return True
    except dbus.DBusException:
        # FIXME: there must be a better way
        dbus_service_path = os.path.abspath(__file__)
        subprocess.Popen(["/usr/bin/python", dbus_service_path]).pid
        # FIXME: hangs Nautilus when booting
        time.sleep(1)
        return True
        
    # Uh... unreachable?
    return False
    
def exit():
    """
    This function is used to exit a running service.
    """
    session_bus = dbus.SessionBus()
    try:
        service = session_bus.get_object(SERVICE, OBJECT_PATH)
        service.Exit()
    except:
        # Probably not running...
        traceback.print_exc()

if __name__ == "__main__":
    # This seems to be important for PySVN
    from nautilussvn.util.helpers import initialize_locale
    initialize_locale()
    
    # The following calls are required to make DBus thread-aware and therefor
    # support the ability run threads.
    gobject.threads_init()
    dbus.glib.threads_init()
    
    # This registers our service name with the bus
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(SERVICE, session_bus) 
    service = Service(session_bus)
    
    # We need this to for the client to be able to do asynchronous calls
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()
    loop.run()