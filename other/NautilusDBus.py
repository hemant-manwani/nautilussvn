"""
Wrote this up in some 30 minutes, allows other programs to query
a DBus service running for which items are selected in Nautilus.

Here's a typical session:

Start the service: 
$ python NautilusDBus.py

Start Nautilus:
$ nautilus -q; nautilus --no-desktop .

Communicate with the DBus service from your application:

import dbus
import dbus.service

INTERFACE = "org.google.code.nautilusdbus.Service"
OBJECT_PATH = "/org/google/code/nautilusdbus/Service"
SERVICE = "org.google.code.nautilussvn.NautilusDBus"

session_bus = dbus.SessionBus()
dbus_service = session_bus.get_object(SERVICE, OBJECT_PATH)

for path in dbus_service.GetSelectedPaths(): print path
"""

import traceback
import subprocess
import sys

# Normally one wouldn't do this but this is a quick hack and I want
# everything in a single file (the nautilus module is only available
# when running inside Nautilus).
if __name__ != "__main__":
    import nautilus

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

INTERFACE = "org.google.code.nautilusdbus.Service"
OBJECT_PATH = "/org/google/code/nautilusdbus/Service"
SERVICE = "org.google.code.nautilussvn.NautilusDBus"

if __name__ != "__main__":
    class NautilusDBus(nautilus.MenuProvider):
        
        def __init__(self):
            def connect_to_dbus():
                self.session_bus = dbus.SessionBus()
                self.dbus_service = self.session_bus.get_object(SERVICE, OBJECT_PATH)
                
            try:
                connect_to_dbus()
            except dbus.DBusException:
                subprocess.Popen(["python", __file__])
                # We'll just assume that the DBus service will be running
                # after this.
                connect_to_dbus()
        
        def get_file_items(self, window, items):            
            if len(items) == 0: 
                # When you deselect everything (e.g. click on the background) 
                # get_file_items is called with 0 items, we can't pass a
                # normal empty Python list though because DBus needs to
                # know the exact type.
                self.dbus_service.SetSelectedPaths(dbus.Array([], "as"))
                return []
            
            # We could convert the uris to actual paths but hey who cares? :-)
            self.dbus_service.SetSelectedPaths([item.get_uri() for item in items])
            
            return [] # Don't think we actually have to return anything per se
            
class Service(dbus.service.Object):
    
    selected_paths = []
    
    def __init__(self, connection):
        dbus.service.Object.__init__(self, connection, OBJECT_PATH)
    
    @dbus.service.method(INTERFACE, in_signature="as", out_signature="")
    def SetSelectedPaths(self, paths):
        self.selected_paths = paths
    
    @dbus.service.method(INTERFACE, in_signature="", out_signature="as")
    def GetSelectedPaths(self):
        # Returns a dbus.Array (as, array of strings)
        return self.selected_paths
        
if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(SERVICE, session_bus) 
    service = Service(session_bus)
    mainloop = gobject.MainLoop()
    mainloop.run()
