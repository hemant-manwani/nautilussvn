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

Our module for everything related to the Nautilus extension.

Known issues:

  - Emblems sometimes don't update untill the selection is modified.
  
    This is caused by threading problems. There's a bunch of FIXME's below 
    with more information.

  - Multiple emblems are attached to a single item which leads to the one
    obscuring the other. So if an item has "normal" status, but it changes to 
    "modified" two emblems are applied and only the emblem "normal" is visible.
    
    How to reproduce:
    
    You need a working copy with at least 2 items (combination doesn't matter).
    
    Use the following working copy (do not open it in Nautilus before doing this):::
    
        mkdir -p /tmp/nautilussvn_testing
        cd /tmp/nautilussvn_testing
        svnadmin create repository
        svn co file:///tmp/nautilussvn_testing/repository working_copy
        touch working_copy/add-this-file
        touch working_copy/or-this-file
    
    Then after adding one of the files move up the tree so you can see the 
    status for the working_copy directory.
  
    Things I researched but weren't the cause (so don't look into these!):
    
      - One idea I had was that because of the C{nautilusVFSFile_table} we might
        have two seperate C{NautilusVFSFile} instances (with different emblems
        attached) pointing to the same file. But that wasn't the case.
  
"""

# TODO: right before releasing move the commentary above to an actual issue 
# report on the tracker and just refer to the Bug #.

import os.path
from os.path import isdir, isfile

import gnomevfs
import nautilus
import pysvn
import gobject
import gtk

from nautilussvn.lib.vcs import create_vcs_instance
from nautilussvn.lib.vcs.svn import SVN
from nautilussvn.lib.dbus.status_monitor import StatusMonitorStub as StatusMonitor
from nautilussvn.lib.helper import split_path
from nautilussvn.lib.decorators import timeit

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ 
    This is the main class that implements all of our awesome features.
    
    """
    
    #: Maps statuses to emblems.
    #: TODO: should probably be possible to create this dynamically
    EMBLEMS = {
        "added" :       "nautilussvn-added",
        "deleted":      "nautilussvn-deleted",
        "modified":     "nautilussvn-modified",
        "conflicted":   "nautilussvn-conflicted",
        "normal":       "nautilussvn-normal",
        "ignored":      "nautilussvn-ignored",
        "locked":       "nautilussvn-locked",
        "read_only":    "nautilussvn-read_only"
    }
    
    
    #: This is our lookup table for C{NautilusVFSFile}s which we need for attaching
    #: emblems. This is mostly a workaround for not being able to turn a path/uri
    #: into a C{NautilusVFSFile}. It looks like:::
    #: 
    #:     nautilusVFSFile_table = {
    #:        "/foo/bar/baz": <NautilusVFSFile>
    #:     
    #:     }
    #: 
    #: Keeping track of C{NautilusVFSFile}s is a little bit complicated because
    #: when an item is moved (renamed) C{update_file_info} doesn't get called. So
    #: we also add C{NautilusVFSFile}s to this table from C{get_file_items} etc.
    nautilusVFSFile_table = {}
    
    #: Keep track of item statuses. This is a workaround for the fact that
    #: emblems added using C{NautilusVFSFile.add_emblem} are removed once the 
    #: C{NautilusVFSFile} is invalidated (one example of when this happens is
    #: when an item is modified).::
    #: 
    #:     statuses = {
    #:         "/foo/bar/baz": "modified"
    #:     }
    #: 
    statuses = {}
    
    def __init__(self):
        # Create a StatusMonitor and register a callback with it to notify us 
        # of any status changes.
        self.status_monitor = StatusMonitor(self.cb_status)
        
    def get_columns(self):
        """
        
        
        """
        
        pass
        
    def update_file_info(self, item):
        """
        
        Normally this function is used to monitor changes to items, however 
        we're using our own C{StatusMonitor} for this. So this function is only
        used to apply emblems (which is needed because emblems from extensions
        are temporary).
        
        C{update_file_info} is called only when:
        
          - When you enter a directory (once for each item) but only when the
            item was modified since the last time it was listed
          - When an item viewable from the current window is created or modified
          
        This is insufficient for our purpose because:
        
          - You're not notified about items you don't see (which is needed to 
            keep the emblem for the directories above the item up-to-date)
        
        When C{update_file_info} is called we do:
        
          - Add the C{NautilusVFSFile} to the lookup table for lookups
          - Add a watch for this item to the C{StatusMonitor} (it's 
            C{StatusMonitor}'s responsibility to check whether this is needed)
        
        What we do to stay up-to-date is:
        
          - We'll notify C{StatusMonitor} of versioning actions (add, commit, lock, 
            unlock etc.), we register callbacks with dialogs for this
        
        When C{StatusMonitor} calls us back we just look the C{NautilusVFSFile} up in
        the look up table using the path and apply an emblem according to the 
        status we've been given.
        
        FIXME: This function is in a race condition with the StatusMonitor
        (which is threaded) to make things update the emblem. For now this
        doesn't seem to be causing any problems (but that doesn't mean anything).
        
        We'll probably have to look into locking and all that stuff.
        
        @type   item: NautilusVFSFile
        @param  item: 
        
        """
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        # Begin debugging code
        print "Debug: update_file_info() called for %s" % path
        # End debugging code
        
        # Always replace the item in the table with the one we receive, because
        # for example if an item is deleted and recreated the NautilusVFSFile
        # we had before will be invalid (think pointers and such).
        self.nautilusVFSFile_table[path] = item
        
        # See comment for variable: statuses
        if path in self.statuses:
            self.set_emblem_by_status(path, self.statuses[path])
            
        self.status_monitor.add_watch(path)
        
    def get_file_items(self, window, items):
        """
        Menu activated with items selected.
        
        Note that calling C{nautilusVFSFile.invalidate_extension_info()} will 
        also cause get_file_items to be called.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   items:  list of NautilusVFSFile
        @param  items:
        
        @rtype:         list of MenuItems
        @return:        The context menu entries to add to the menu.
        
        """
        
        if len(items) == 0: return
        
        paths = []
        for item in items:
            if item.get_uri().startswith("file://"):
                path = gnomevfs.get_local_path_from_uri(item.get_uri())
                paths.append(path)
                self.nautilusVFSFile_table[path] = item
        
        return MainContextMenu(paths, self).construct_menu()
        
    def get_background_items(self, window, item):
        
        """
        Menu activated on entering a directory. Builds context menu for File
        menu and for window background.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   item:   NautilusVFSFile
        @param  item:
        
        @rtype:         list of MenuItems
        @return:        The context menu entries to add to the menu.
        
        """
        
        if not item.get_uri().startswith("file://"): return
        path = gnomevfs.get_local_path_from_uri(item.get_uri())
        
        # Begin debugging code
        print "Debug: get_background_items() for %s" % path
        # End debugging code
        
        self.nautilusVFSFile_table[path] = item
        
        # FIXME:
        # This is a hack to try and work around the multiple emblems on a single
        # item bug. Since get_background_items is called once when you enter
        # a directory we just invalidate all items immediately below it.
        
        # MARKER: performance 
        parent_path = split_path(path)
        if parent_path in self.nautilusVFSFile_table:
            item = self.nautilusVFSFile_table[parent_path]
            item.invalidate_extension_info()
        
        for child_basename in os.listdir(path):
            child_path = os.path.join(path, child_basename)
            if child_path in self.nautilusVFSFile_table:
                # Begin debugging code
                print "Debug: invalidated %s in get_background_items()" % child_basename
                # End debugging code
                child_item = self.nautilusVFSFile_table[child_path]
                # FIXME: still doesn't work but committing to save
                child_item.invalidate_extension_info()
        
        return MainContextMenu([path], self).construct_menu()
    
    #
    # Helper functions
    #
    
    def set_emblem_by_status(self, path, status):
        """
        Set the emblem for a path by status. 
        
        @type   path: string
        @param  path: The path for which to set the emblem.
        
        @type   status: string
        @param  status: A string indicating the status of an item (see: EMBLEMS).
        """
        
        # Try and lookup the NautilusVFSFile in the lookup table since we need it
        # TODO: should we remove this? This function is only called by 
        # update_file_info so this should be guaranteed.
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # Begin debugging code
        print "Debug: set_emblem_by_status() called for %s with status %s" % (path, status)
        # End debugging code
        
        if status in self.EMBLEMS:
            item.add_emblem(self.EMBLEMS[status])
    
    #
    # Callbacks
    #
    
    def cb_status(self, path, status):
        """
        This is the callback that C{StatusMonitor} calls. 
        
        @type   path: string
        @param  path: The path of the item something interesting happend to.
        
        @type   status: string
        @param  status: A string indicating the status of an item (see: EMBLEMS).
        """
        
        # Begin debugging code
        print "Debug: cb_status() called for %s with status %s" % (path, status)
        # End debugging code
        
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # See comment for variable: statuses
        # There's no reason to do a lot of stuff if the emblem is the same
        # but since we're the only function who does a add_emblem, we have to.
        
        self.statuses[path] = status
        
        # We need to invalidate the extension info for only one reason:
        #
        # - Invalidating the extension info will cause Nautilus to remove all
        #   temporary emblems we applied so we don't have overlay problems
        #   (with ourselves, we'd still have some with other extensions).
        #
        # FIXME: for some reason the invalidate_extension_info isn't always 
        # processed and update_file_info isn't called. So as a workaround we
        # already set the emblem, running the risk of applying multiple emblems
        # at the same time which overlap potentially resulting in the actual 
        # status of an item not being displayed.
        #
        self.set_emblem_by_status(path, status)
        item.invalidate_extension_info()
    
class MainContextMenu():
    """
    
    A class that represents our context menu.
    
    See: http://code.google.com/p/nautilussvn/wiki/ContextMenuStructure
    
    FIXME: There's currently a problem with the order in which menu items 
    appear, even though a list such as C{[<Update>, <Commit>, <NautilusSvn>]} 
    would be returned it might end up as C{[<NautilusSvn>, <Update>, <Commit>]}.
    
    """
    
    def __init__(self, paths, nautilussvn_extension):
        self.paths = paths
        self.nautilussvn_extension = nautilussvn_extension
        self.vcs_client = create_vcs_instance()
        
    def construct_menu(self):
        """
        
        This function is really only used to contain the menu defintion. The
        actual menu is build using C{create_menu_from_definition}.
        
        @rtype:     list of MenuItems
        @return:    A list of MenuItems representing the context menu.
        """
        
        # The following dictionary defines the complete contextmenu
        menu_definition = [
            {
                "identifier": "NautilusSvn::Debug",
                "label": "Debug",
                "tooltip": "",
                "icon": "nautilussvn-monkey",
                "signals": {
                    "activate": {
                        "callback": None,
                        "args": None
                    }
                },
                "condition": (lambda: True),
                "submenus": [
                    {
                        "identifier": "NautilusSvn::Debug_Asynchronicity",
                        "label": "Test Asynchronicity",
                        "tooltip": "",
                        "icon": "nautilussvn-asynchronous",
                        "signals": {
                            "activate": {
                                "callback": self.callback_debug_asynchronicity,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
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
                        "icon": "nautilussvn-refresh",
                        "signals": {
                            "activate": {
                                "callback": self.callback_refresh_status,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Debug_Revert",
                        "label": "Debug Revert",
                        "tooltip": "Reverts everything it sees",
                        "icon": "nautilussvn-revert",
                        "signals": {
                            "activate": {
                                "callback": self.callback_debug_revert,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Debug_Invalidate",
                        "label": "Invalidate",
                        "tooltip": "Force a invalidate_extension_info() call",
                        "icon": "nautilussvn-clear",
                        "signals": {
                            "activate": {
                                "callback": self.callback_debug_invalidate,
                                "args": None
                            }
                        },
                        "condition": (lambda: True),
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Debug_Add_Emblem",
                        "label": "Add Emblem",
                        "tooltip": "Add an emblem",
                        "icon": "nautilussvn-emblems",
                        "signals": {
                            "activate": {
                                "callback": self.callback_debug_add_emblem,
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
                "icon": "nautilussvn-checkout",
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
                "icon": "nautilussvn-update",
                "signals": {
                    "activate": {
                        "callback": self.callback_update,
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
                "icon": "nautilussvn-commit",
                "signals": {
                    "activate": {
                        "callback": self.callback_commit,
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
                        "icon": "nautilussvn-diff",
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
                        "icon": "nautilussvn-show_log",
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
                        "icon": "nautilussvn-add",
                        "signals": {
                            "activate": {
                                "callback": self.callback_add,
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
                        "icon": "nautilussvn-rename",
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
                        "icon": "nautilussvn-delete",
                        "signals": {
                            "activate": {
                                "callback": self.callback_delete,
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
                        "icon": "nautilussvn-revert",
                        "signals": {
                            "activate": {
                                "callback": self.callback_revert,
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
                        "icon": "nautilussvn-properties",
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
                        "icon": "nautilussvn-help",
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
                        "icon": "nautilussvn-settings",
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
                        "icon": "nautilussvn-about",
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
        
        Create the actual menu from a menu definiton.
        
        A single menu item definition looks like::
        
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
        
        @type   menu_definition:  list
        @param  menu_definition:  A list of definition items.
        
        @rtype:     list of MenuItems
        @return:    A list of MenuItems representing the context menu.
        
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
        if (len(self.paths) == 1 and
                isdir(self.paths[0]) and
                not self.vcs_client.is_working_copy(self.paths[0])):
            return True
            
        return False
        
    def condition_update(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path) and
                    not self.vcs_client.is_added(path)):
                return True
                
        return False
        
    def condition_commit(self):
        for path in self.paths:
            if self.vcs_client.is_in_a_or_a_working_copy(path): 
                if (self.vcs_client.is_added(path) or 
                        self.vcs_client.is_modified(path) or
                        self.vcs_client.is_deleted(path)):
                    return True
                else:
                    if (isdir(path) and
                            (self.vcs_client.has_added(path) or 
                            self.vcs_client.has_modified(path) or
                            self.vcs_client.has_deleted(path))):
                        return True
        
        return False
        
    def condition_diff(self):
        if len(self.paths) == 2:
            return True
        elif (len(self.paths) == 1 and 
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]) and
                self.vcs_client.is_modified(self.paths[0])):
            return True
        
        return False
        
    def condition_show_log(self):
        if (len(self.paths) == 1 and
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]) and
                self.vcs_client.is_versioned(self.paths[0]) and
                not self.vcs_client.is_added(self.paths[0])):
            return True
        
        return False
        
    def condition_add(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    not self.vcs_client.is_versioned(path)):
                return True
            else:
                if (isdir(path) and
                        self.vcs_client.is_in_a_or_a_working_copy(path) and
                        self.vcs_client.has_unversioned(path)):
                    return True
            
        return False
        
    def condition_add_to_ignore_list(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return False
                
        return True
        
    def condition_rename(self):
        if (len(self.paths) == 1 and
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]) and
                self.vcs_client.is_versioned(self.paths[0]) and
                not self.vcs_client.is_added(self.paths[0])):
            return True
        
        return False
        
    def condition_delete(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
            
        return False
        
    def condition_revert(self):
        for path in self.paths:
            if self.vcs_client.is_in_a_or_a_working_copy(path): 
                if (self.vcs_client.is_added(path) or 
                        self.vcs_client.is_modified(path) or
                        self.vcs_client.is_deleted(path)):
                    return True
                else:
                    if (isdir(path) and
                            (self.vcs_client.has_added(path) or 
                            self.vcs_client.has_modified(path) or
                            self.vcs_client.has_deleted(path))):
                        return True
        
        return False
        
    def condition_blame(self):
        if (len(self.paths) == 1 and
                self.vcs_client.is_in_a_or_a_working_copy(path) and
                self.vcs_client.is_versioned(self.paths[0]) and
                not self.vcs_client.is_added(self.paths[0])):
            return True
        
        return False
        
    def condition_properties(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
        
        return False
        
    #
    # Callbacks
    #
    
    # Begin debugging callbacks
    def callback_debug_asynchronicity(self, menu_item, paths):
        """
        This is a function to test doing things asynchronously.
        
        Plain Python threads don't seem to work properly in the context of a
        Nautilus extension, so this doesn't work out all too well::
        
            import thread
            thread.start_new_thread(asynchronous_function, ())
        
        The thread will _only_ run when not idle (e.g. it will run for a short 
        while when you change the item selection).
        
        A few words of advice. Don't be misled, as I was, into thinking that a 
        function you add using C{gobject.add_idle} is run asynchronously. 
        
        Calling C{time.sleep()} or doing something for a long time will simply block 
        the main thread while the function is running. It's just that Nautilus
        is idle a lot so it might create that impression.
        
        Calling C{gtk.gdk.threads_init()} or C{gobject.threads_init()} is not needed.
        
        Also see:
        
          - http://www.pygtk.org/pygtk2reference/gobject-functions.html
          - http://www.pygtk.org/docs/pygtk/gdk-functions.html
        
        Interesting links (but not relevant per se): 
        
          - http://research.operationaldynamics.com/blogs/andrew/software/gnome-desktop/gtk-thread-awareness.html
          - http://unpythonic.blogspot.com/2007/08/using-threads-in-pygtk.html
        
        """
    
        import thread
        import time
        
        def asynchronous_function():
            print "Debug: inside asynchronous_function()"
            
            for i in range(0, 100000):
                print i
            
            print "Debug: asynchronous_function() finished"
        
        # Calling threads_init does not do anything.
        gobject.threads_init()
        thread.start_new_thread(asynchronous_function, ())
        
    def callback_debug_shell(self, menu_item, paths):
        """
        
        Open up an IPython shell which shares the context of the extension.
        
        See: http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
        
        """
        import gtk
        from nautilussvn.debug.ipython_view import IPythonView
        
        window = gtk.Window()
        window.set_size_request(750,550)
        window.set_resizable(True)
        window.set_position(gtk.WIN_POS_CENTER)
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
    
    def callback_refresh_status(self, menu_item, paths):
        nautilussvn_extension = self.nautilussvn_extension
        status_monitor = nautilussvn_extension.status_monitor
        for path in paths:
            status_monitor.status(path, invalidate=True)
    
    def callback_debug_revert(self, menu_item, paths):
        for path in paths:
            # Normal revert
            self.callback_revert(menu_item, paths)
            # Super revert
            statuses = self.vcs_client.status_with_cache(path, invalidate=True)[:-1]
            for status in statuses:
                if status == pysvn.wc_status_kind.missing:
                    self.callback_revert(
                        menu_item,
                        os.path.join(path, status.data["path"])
                    )
        
    def callback_debug_invalidate(self, menu_item, paths):
        nautilussvn_extension = self.nautilussvn_extension
        nautilusVFSFile_table = nautilussvn_extension.nautilusVFSFile_table
        for path in paths:
            # Begin debugging code
            print "Debug: callback_debug_invalidate() called for %s" % path
            # End debugging code
            if path in nautilusVFSFile_table:
                nautilusVFSFile_table[path].invalidate_extension_info()
    
    def callback_debug_add_emblem(self, menu_item, paths):
        def add_emblem_dialog():
            from subprocess import Popen, PIPE
            command = ["zenity", "--entry", "--title=NautilusSVN", "--text=Emblem to add:"]
            emblem = Popen(command, stdout=PIPE).communicate()[0].replace("\n", "")
            
            nautilussvn_extension = self.nautilussvn_extension
            nautilusVFSFile_table = nautilussvn_extension.nautilusVFSFile_table
            for path in paths:
                if path in nautilusVFSFile_table:
                    nautilusVFSFile_table[path].add_emblem(emblem)
            return False
            
        gobject.idle_add(add_emblem_dialog)        
    
    # End debugging callbacks
    
    def callback_update(self, menu_item, paths):
        client = pysvn.Client()
        for path in paths:
            client.update(path)
        self.callback_refresh_status(menu_item, paths)

    def callback_commit(self, menu_item, paths):
        def commit_dialog():
            from subprocess import Popen, PIPE
            command = ["zenity", "--entry", "--title=NautilusSVN", "--text=Log message:"]
            log_message = Popen(command, stdout=PIPE).communicate()[0]
            
            client = pysvn.Client()
            client.checkin(paths, log_message)
            self.callback_refresh_status(menu_item, paths)
            
            return False
        
        gobject.idle_add(commit_dialog)
        

    def callback_add(self, menu_item, paths):
        """
        Put files and directories under version control, scheduling
        them for addition to repository. They will be added in next commit.
        
        If paths only contains files then the files are added directly, 
        otherwise an Add dialog is instantiated.
        
        @type   menu_item: nautilus.MenuItem
        @param  menu_item: The menu item that was selected.
        
        @type   paths: list
        @param  paths: A list of paths to add.
        """
        
        client = pysvn.Client()
        for path in paths:
            client.add(path)
        self.callback_refresh_status(menu_item, paths)

    def callback_delete(self, menu_item, paths):
        # FIXME: 
        #   - ClientError has local modifications
        #   - ClientError is not under version control
        #   - ClientERror has local modifications
        client = pysvn.Client()
        for path in paths:
            client.remove(path)
        self.callback_refresh_status(menu_item, paths)

    def callback_revert(self, menu_item, paths):
        # TODO: if called on a directory should revert also revert items that
        # were svn added, but then manually deleted (resulting in missing)? See
        # callback_debug_revert.
        client = pysvn.Client()
        for path in paths:
            client.revert(path)
        self.callback_refresh_status(menu_item, paths)
