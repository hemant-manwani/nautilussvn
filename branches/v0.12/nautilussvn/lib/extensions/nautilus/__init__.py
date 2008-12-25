#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006 Jason Field
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
# along with NautilusSvn; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import os.path
from os.path import isdir, isfile

import gnomevfs
import nautilus
import pysvn
import gobject

import nautilussvn.lib.vcs 

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ 
    This is the main class that implements all of our awesome features.
    
    """
    
    # Maps statuses to emblems
    EMBLEMS = {
        "added" : "emblem-added",
        "deleted": "emblem-deleted",
        "modified": "emblem-modified",
        "conflicted": "embled-conflicted",
        "normal": "emblem-normal"
    }
    
    # This is our lookup table for NautilusVFSFiles which we need for attaching
    # emblems. his is mostly a workaround for not being able to turn a path/uriT
    # into a NautilusVFSFile.
    nautilusVFSFile_table = {}
    
    # Keep track of item statuses. This is a workaround for the emblem added
    # using add_emblem being only temporary, it's used in update_file_info.
    statuses = {}
    
    # This is a dictionary we use to keep track of everything that's interesting
    # debugging wise.
    debugging_information = {
        "items": {}
    }
    
    def __init__(self):
        # Create a StatusMonitor and register a callback with it to notify us 
        # of any status changes.
        self.status_monitor = StatusMonitor(self.update_emblem)
        
    def get_columns(self):
        """
        
        
        """
        
        pass
        
    def update_file_info(self, item):
        """
        
        update_file_info is called only when:
        
          * When you enter a directory (once for each item)
          * When an item viewable from the current window is created or modified
          
        This is insufficient for our purpose because:
        
          * You're not notified about items you don't see (which is needed to 
            keep the emblem for the directories above the item up-to-date)
        
        When update_file_info is called we do:
        
          * Add the NautilusVFSFile to the lookup table for lookups
          * Add a watch for this item to the StatusMonitor (it's StatusMonitor's
            responsibility to check whether this is needed)
        
        What we do to stay up-to-date is:
        
          * We'll notify StatusMonitor of versioning actions (add, commit, lock, 
            unlock etc.), we register callbacks with dialogs for this
        
        When StatusMonitor calls us back we just look the NautilusVFSFile up in
        the look up table using the path and apply an emblem according to the 
        status we've been given.
        
        @type   item: NautilusVFSFile
        @param  item: 
        
        """
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        if not path in self.nautilusVFSFile_table:
            self.nautilusVFSFile_table[path] = item
        
        # Begin debugging code
        if not path in self.debugging_information["items"]:
            self.debugging_information["items"][path] = {
                "added_emblems": []
            }
        else:
            self.debugging_information["items"][path]["added_emblems"] = []
        # End debugging code
        
        # See comment for variable: statuses
        if path in self.statuses:
            self.update_emblem(path, self.statuses[path], invalidate=False)
            
        self.status_monitor.add_watch(path)
        
    def get_file_items(self, window, items):
        """
        Menu activated with items selected.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   items: list of NautilusVFSFile
        @param  items:
        
        """
        
        if len(items) == 0: return
        paths = [gnomevfs.get_local_path_from_uri(item.get_uri()) for item in items 
            if item.get_uri().startswith("file://")]
        
        return MainContextMenu(paths, self).construct_menu()
        
    def get_background_items(self, window, item):
        """
        Menu activated on window background.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   item:   NautilusVFSFile
        @param  item:
        
        """
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        return MainContextMenu([path], self).construct_menu()
        
    #
    # Callbacks
    #
    
    def update_emblem(self, path, status, invalidate=True):
        """
        
        @type   invalidate: boolean
        @param  invalidate: Whether or not to invalidate the item found
        
        """
        
        # See comment for variable: statuses
        self.statuses[path] = status
        
        # Try and lookup the NautilusVFSFile in the lookup table since we need it
        if not path in self.nautilusVFSFile_table: return
        
        item = self.nautilusVFSFile_table[path]
        if status in self.EMBLEMS:
            item.add_emblem(self.EMBLEMS[status])
            
            # Begin debugging code
            if path in self.debugging_information["items"]:
                self.debugging_information["items"][path]["added_emblems"].append(self.EMBLEMS[status])
            # End debugging code
            
        # We need to invalidate the extension info because the emblem added
        # through add_emblem is only temporary, also see the comment for 
        # variable: statuses
        if invalidate: item.invalidate_extension_info()
    
class MainContextMenu():
    """
    
    See: http://code.google.com/p/nautilussvn/wiki/ContextMenuStructure
    
    """
    
    def __init__(self, paths, nautilussvn_extension):
        self.paths = paths
        self.nautilussvn_extension = nautilussvn_extension
        
    def construct_menu(self):
        """
        
        """
        
        # The following dictionary defines the complete contextmenu
        menu_definition = [
            {
                "identifier": "NautilusSvn::Debug",
                "label": "Debug",
                "tooltip": "",
                "icon": "icon-monkey",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                },
                "condition": (lambda: True),
                "submenus": [
                    {
                        "identifier": "NautilusSvn::Debug_Shell",
                        "label": "Open Shell",
                        "tooltip": "",
                        "icon": "gnome-terminal",
                        "signals": {
                            "activate": {
                                "callback": self.callback_debug_shell,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Refresh_Status",
                        "label": "Refresh Status",
                        "tooltip": "",
                        "icon": "icon-refresh",
                        "signals": {
                            "activate": {
                                "callback": self.callback_refresh_status,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    }
                ]
            },
            {
                "identifier": "NautilusSvn::Checkout",
                "label": "Checkout",
                "tooltip": "",
                "icon": "icon-checkout",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                }, 
                "condition": self.condition_checkout,
                "submenus": [
                    
                ]
            },
            {
                "identifier": "NautilusSvn::Update",
                "label": "Update",
                "tooltip": "",
                "icon": "icon-update",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                }, 
                "condition": self.condition_update,
                "submenus": [
                    
                ]
            },
            {
                "identifier": "NautilusSvn::Commit",
                "label": "Commit",
                "tooltip": "",
                "icon": "icon-commit",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                }, 
                "condition": self.condition_commit,
                "submenus": [
                    
                ]
            },
            {
                "identifier": "NautilusSvn::NautilusSvn",
                "label": "NautilusSvn",
                "tooltip": "",
                "icon": "nautilussvn",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                }, 
                "condition": (lambda: True),
                "submenus": [
                    {
                        "identifier": "NautilusSvn::Diff",
                        "label": "Diff",
                        "tooltip": "",
                        "icon": "icon-diff",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_diff,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Show_Log",
                        "label": "Show Log",
                        "tooltip": "",
                        "icon": "icon-show_log",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_show_log,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Add",
                        "label": "Add",
                        "tooltip": "",
                        "icon": "icon-add",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_add,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Rename",
                        "label": "Rename",
                        "tooltip": "",
                        "icon": "icon-rename",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_rename,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Delete",
                        "label": "Delete",
                        "tooltip": "",
                        "icon": "icon-delete",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_delete,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Revert",
                        "label": "Revert",
                        "tooltip": "",
                        "icon": "icon-revert",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_revert,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Properties",
                        "label": "Properties",
                        "tooltip": "",
                        "icon": "icon-properties",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_properties,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Help",
                        "label": "Help",
                        "tooltip": "",
                        "icon": "icon-help",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Settings",
                        "label": "Settings",
                        "tooltip": "",
                        "icon": "icon-settings",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::About",
                        "label": "About",
                        "tooltip": "",
                        "icon": "icon-about",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    }
                ]
            },
        ]
        
        return self.create_menu_from_definition(menu_definition)
    
    def create_menu_from_definition(self, menu_definition):
        """
        
        A single menu item definition looks like:
            {
                "identifier": "NautilusSvn::Identifier",
                "label": "",
                "tooltip": "",
                "icon": "",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                }, 
                "condition": None,
                "submenus": [
                    
                ]
            }
        
        @type   menu_definition  list
        @param  menu_definition  A list of definition items.
        
        """
        
        menu = []
        for definition_item in menu_definition:
            if definition_item["condition"]():
                menu_item = nautilus.MenuItem(
                    definition_item["identifier"],
                    definition_item["label"],
                    definition_item["tooltip"],
                    definition_item["icon"]
                )
                
                for signal, value in definition_item["signals"].items():
                    if value["callback"] != None:
                        menu_item.connect(signal, value["callback"], self.paths)
                
                menu.append(menu_item)
                
                # Since we can't just call set_submenu and run the risk of not
                # having any submenu items later (which would result in the 
                # menu item not being displayed) we have to check first.
                submenu = self.create_menu_from_definition(
                    definition_item["submenus"]
                )
                
                if len(submenu) > 0:
                    nautilus_submenu = nautilus.Menu()
                    menu_item.set_submenu(nautilus_submenu)
                    
                    for submenu_item in submenu:
                        nautilus_submenu.append_item(submenu_item)
        
        return menu
    #
    # Conditions
    #
    
    def condition_checkout(self):
        return False
        
    def condition_update(self):
        return False
        
    def condition_commit(self):
        return False
        
    def condition_diff(self):
        return False
        
    def condition_show_log(self):
        return False
        
    def condition_add(self):
        return False
        
    def condition_add_to_ignore_list(self):
        return False
        
    def condition_rename(self):
        return False
        
    def condition_delete(self):
        return False
        
    def condition_revert(self):
        return False
        
    def condition_blame(self):
        return False
        
    def condition_properties(self):
        return False
        
    #
    # Callbacks
    #
    
    def callback_debug_shell(self, menu_item, paths):
        """
        
        Open up an IPython shell which shares the context of the extension.
        
        See: http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
        
        """
        
        # TODO: use a Glade file for most of this instead.
        import gtk
        from nautilussvn.debug.ipython_view import IPythonView
        
        window = gtk.Window()
        window.set_size_request(750,550)
        window.set_resizable(True)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        ipython_view = IPythonView()
        ipython_view.updateNamespace(locals())
        ipython_view.set_wrap_mode(gtk.WRAP_CHAR)
        ipython_view.show()
        scrolled_window.add(ipython_view)
        scrolled_window.show()
        window.add(scrolled_window)
        window.show()
        window.connect('delete_event', lambda x,y: False)
        window.connect('destroy', lambda x: gtk.main_quit())
        gtk.main()
    
    def callback_refresh_status(self, menu_item, paths):
        nautilussvn_extension = self.nautilussvn_extension
        status_monitor = nautilussvn_extension.status_monitor
        for path in paths:
            status_monitor.status(path)

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

class StatusMonitor():
    """
    
    What StatusMonitor does:
    
    * When somebody adds a watch and if there's not already a watch for this 
      item it will add one and do an initial status check.
    
    * Use inotify to keep track of modifications of any watched items
        (we actually only care about modifications not creations and deletions)
        
    * Either on request, or when something interesting happens, it checks
      the status for an item which means:
        
        * See working code for exactly what a status check means
        
        * After checking the status for an item, if there's a watch for
          a parent directory this is what will happen:    
        
          * If status is (vcs) modified, (vcs) added or (vcs) deleted:
            - for every parent the callback will be called with status 
              "modified" (since it cannot be any other way)
          
          * If vcs status is normal: 
            - a status check is done for the parent directory since we 
              cannot be sure what the status for them is
      
    In the future we might implement a functionality which also monitors
    versioning actions so the command-line client can be used and still have
    the emblems update accordingly. 
    
    """
    
    # TODO: this is the reverse of STATUS in the svn module and should probably
    # be moved there once I figure out what the responsibilities for the svn
    # module are.
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
    
    # A dictionary to keep track of the paths we're watching
    watches = {}
    
    # The mask for the inotify events we're interested in
    mask = EventsCodes.IN_MODIFY
    
    class VCSProcessEvent(ProcessEvent):
        """
        
        Our processing class for inotify events.
        
        """
        
        def __init__(self, status_monitor):
            self.status_monitor = status_monitor
            self.vcs_client = nautilussvn.lib.vcs.create_vcs_instance()
        
        def process_IN_MODIFY(self, event):
            path = event.path
            if event.name: path = os.path.join(path, event.name)
            
            # Begin debugging code
            print "Event triggered for: %s" % path.rstrip(os.pathsep)
            # End debugging code
            
            # Make sure to strip any trailing slashes because that will 
            # cause problems for the status checking
            # TODO: not 100% sure about it causing problems
            if self.vcs_client.is_in_a_or_a_working_copy(path):
                self.status_monitor.status(path.rstrip(os.pathsep))
    
    def __init__(self, callback):
        self.callback = callback
        
        self.vcs_client = nautilussvn.lib.vcs.create_vcs_instance()
        
        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(
            self.watch_manager, self.VCSProcessEvent(self))
        self.notifier.start()
        
    def add_watch(self, path):
        if not path in self.watches:
            # We can safely ignore items that aren't inside a working_copy or
            # a working copy administration area (.svn)
            if (path.find(".svn") > 0 or 
                    self.vcs_client.is_in_a_or_a_working_copy(path)):
                self.watches[path] = None # don't need a value
                # TODO: figure out precisely how this watch is added. Does it:
                #
                #  * Recursively register watches
                #  * Call the process method with the path argument originally used
                #    or with the path for the specific item that was modified.
                # 
                # FIXME: figure out why when registering a parent directory and the 
                # file itself the IN_MODIFY event handler is called 3 times (once 
                # for the directory and twice for the file itself).
                #
                self.watch_manager.add_watch(path, self.mask, rec=True)
                
                # But we shouldn't do any status checks on files in the working
                # copy administration area.
                if self.vcs_client.is_in_a_or_a_working_copy(path):
                    self.status(path)
            
    def status(self, path):
        
        def split_path(path):
            """
            
            Sorta lot like os.path.split, but removes any trailing pathseps.
            
            >>> split_path("/foo/bar/baz")
            '/foo/bar'
            
            """
            
            path = path.rstrip(os.path.sep)
            return path[:path.rfind(os.path.sep)]
        
        client = pysvn.Client()
        
        # If we're not a or inside a working copy we don't even have to bother.
        if not self.vcs_client.is_in_a_or_a_working_copy(path): return
        
        # A directory should have a modified status when any of its children
        # have a certain status (see modified_statuses below). Jason thought up 
        # of a nifty way to do this by using sets and the bitwise AND operator (&).
        if isdir(path):
            modified_statuses = set([
                pysvn.wc_status_kind.added, 
                pysvn.wc_status_kind.deleted, 
                pysvn.wc_status_kind.modified
            ])
            statuses = set([status.data["text_status"] for status in client.status(path)][:-1])
            if len(modified_statuses & statuses): 
                self.callback(path, "modified")
                while path != "":
                    path = split_path(path)
                    self.callback(path, "modified")
                return;
        
        # Verifiying the rest of the statuses is common for both files and directories.
        status = client.status(path, depth=pysvn.depth.empty)[0].data["text_status"]
        if status in self.STATUS:
            self.callback(path, self.STATUS[status])
            while path != "":
                path = split_path(path)
                if status in (
                    pysvn.wc_status_kind.added, 
                    pysvn.wc_status_kind.deleted, 
                    pysvn.wc_status_kind.modified,
                ):
                    self.callback(path, "modified")
                elif status in (
                        pysvn.wc_status_kind.normal,
                        pysvn.wc_status_kind.unversioned,
                    ):
                    self.status(path)
