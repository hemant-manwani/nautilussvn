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

import os.path

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

class StatusMonitor():
    """
    
    """

    #: The mask for the inotify events we're interested in.
    #: TODO: understand how masking works
    #: TODO: maybe we should just analyze StatusProcessEvent and determine this 
    #: dynamically because one might tend to forgot to update these
    mask = EventsCodes.IN_MODIFY | EventsCodes.IN_MOVED_TO
    
    class StatusProcessEvent(ProcessEvent):
        """
        
        Our processing class for inotify events.
        
        """
        
        def __init__(self, callback):
            self.callback = callback
        
        def process(self, event):
            path = event.path
            if event.name: path = os.path.join(path, event.name)
            
            # Begin debugging code
            print "Debug: Event %s triggered for: %s" % (event.event_name, path.rstrip(os.path.sep))
            # End debugging code
            
            # Make sure to strip any trailing slashes because that will 
            # cause problems for the status checking
            # TODO: not 100% sure about it causing problems
            self.callback(path.rstrip(os.path.sep))
    
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
        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(
            self.watch_manager, self.StatusProcessEvent(self.callback))
        self.notifier.start()
        
    def add_watch(self, path):
        self.watch_manager.add_watch(path, self.mask, rec=True)
