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
  
    This is either caused by threading problems or update_file_info not being 
    called. There's a bunch of FIXME's below with more information.
    
    A quick workaround for this that might work:
    
      - At the moment we're _only_ using our inotify handler to let us know
        when something changes. This is a workaround for C{update_file_info}'s
        limitations. We're basically only using C{update_file_info} to apply the 
        emblem. However, C{update_file_info} works perfectly to let us know
        an item we're currently viewing modified.
        
        So the workaround is to use that... next to the inotify handler.
        
        The inotify handler will be used to let us know of things we can't see
        and C{update_file_info} for those things that we can see.

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

import nautilussvn.lib.vcs
from nautilussvn.lib.helper import split_path

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
        #~ print "Debug: cb_status() called for %s with status %s" % (path, status)
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
        self.vcs_client = nautilussvn.lib.vcs.create_vcs_instance()
        
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
            # If you do:
            # 
            #   tail -f /tmp/nautilussvn/counterlog
            #
            # You will notice that the thread is only run for a short while.
            print "Debug: inside asynchronous_function()"
            
            temporary_directory = "/tmp/nautilussvn"
            if not os.path.isdir(temporary_directory): os.mkdir(temporary_directory)
            file = open(os.path.join(temporary_directory, "counterlog"), "w")
            
            for i in range(0, 100000):
                print i
                file.write(str(i) + "\n")
            
            file.close()    
            print "Debug: asynchronous_function() finished"
            
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

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

class StatusMonitor():
    """
    
    The C{StatusMonitor} is basically a replacement for the currently limited 
    C{update_file_info} function.
    
    What C{StatusMonitor} does:
    
      - When somebody adds a watch and if there's not already a watch for this 
        item it will add one and do an initial status check.
    
      - Use inotify to keep track of modifications of any watched items
        (we actually only care about modifications not creations and deletions)
        
      - Either on request, or when something interesting happens, it checks
        the status for an item which means:
        
          - See working code for exactly what a status check means
        
          - After checking the status for an item, if there's a watch for
            a parent directory this is what will happen:    
        
              - If status is (vcs) modified, (vcs) added or (vcs) deleted:
            
                  - For every parent the callback will be called with status 
                    "modified" (since it cannot be any other way)
          
              - If vcs status is normal: 
            
                  - A status check is done for the parent directory since we 
                    cannot be sure what the status for them is
      
    In the future we might implement a functionality which also monitors
    versioning actions so the command-line client can be used and still have
    the emblems update accordingly. 
    
    UML sequence diagram depicting how the StatusMonitor is used::

        +---------------+          +-----------------+         
        |  NautilusSVN  |          |  StatusMonitor  |         
        +---------------+          +-----------------+         
               |                            |                  
               |   new(self.cb_status)      |                  
               |--------------------------->|                  
               |                            |                  
               |     add_watch(path)        |                  
               |--------------------------->|---+              
               |                            |   |              
               |  cb_status(path, status)   |   | status(path) 
               |<---------------------------|<--+              
               |                            |                  
               |---+                        |                  
               |   | set_emblem_by_status(path, status)      
               |<--+                        |                  
               |                            |                  

    
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
    
    #: The mask for the inotify events we're interested in.
    #: TODO: understand how masking works
    #: TODO: maybe we should just analyze VCSProcessEvent and determine this 
    #: dynamically because one might tend to forgot to update these
    mask = EventsCodes.IN_MODIFY | EventsCodes.IN_MOVED_TO
    
    class VCSProcessEvent(ProcessEvent):
        """
        
        Our processing class for inotify events.
        
        """
        
        def __init__(self, status_monitor, vcs_client):
            self.status_monitor = status_monitor
            self.vcs_client = vcs_client
        
        def process(self, event):
            path = event.path
            if event.name: path = os.path.join(path, event.name)
            
            # Begin debugging code
            print "Debug: Event %s triggered for: %s" % (event.event_name, path.rstrip(os.path.sep))
            # End debugging code
            
            # Subversion (pysvn? svn?) makes temporary files for some purpose which
            # are detected by inotify but are deleted shortly thereafter. So we
            # ignore them.
            # TODO: this obviously doesn't account for the fact that people might
            # version files with a .tmp extension.
            if path.endswith(".tmp"): return
            
            # Make sure to strip any trailing slashes because that will 
            # cause problems for the status checking
            # TODO: not 100% sure about it causing problems
            if self.vcs_client.is_in_a_or_a_working_copy(path):
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
    
    def __init__(self, callback):
        self.callback = callback
        
        self.vcs_client = nautilussvn.lib.vcs.create_vcs_instance()
        
        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(
            self.watch_manager, self.VCSProcessEvent(self, self.vcs_client))
        self.notifier.start()
    
    def add_watch(self, path):
        """
        
        Request a watch to be added for path. This function will figure out
        the best spot to add the watch (most likely a parent directory).
        
        TODO: refactor to remove code duplication
        MARKER: performance 
        
        """
        
        if not path in self.watches:
            # We can safely ignore items that aren't inside a working_copy or
            # a working copy administration area (.svn)
            if (path.find(".svn") > 0 or 
                    self.vcs_client.is_in_a_or_a_working_copy(path)):
                self.watches[path] = None # don't need a value
                # TODO: figure out precisely how this watch is added. Does it:
                #
                #  - Recursively register watches
                #  - Call the process method with the path argument originally used
                #    or with the path for the specific item that was modified.
                # 
                # FIXME: figure out why when registering a parent directory and the 
                # file itself the IN_MODIFY event handler is called 3 times (once 
                # for the directory and twice for the file itself).
                #
                
                # We only have to add a full recursive watch once, then we just
                # add new watches dynamically when events are triggered. So look
                # up to see whether there's already a watch set.
                
                # MARKER: performance 
                path_to_check = path
                watch_is_already_set = False
                while path_to_check !="":
                    path_to_check = split_path(path_to_check)
                    if path_to_check in self.watches:
                        watch_is_already_set = True
                        break;
                
                # To always be able to track moves (renames are moves too) we 
                # have to make sure we register with our parent directory
                if not watch_is_already_set:
                    parent_path = split_path(path)
                    
                    if (parent_path.find(".svn") > 0 or 
                            self.vcs_client.is_in_a_or_a_working_copy(parent_path)):
                        path_to_be_watched = parent_path
                    else:
                        path_to_be_watched = path
                    
                    self.watch_manager.add_watch(path_to_be_watched, self.mask, rec=True)
                    # Begin debugging code
                    print "Debug: StatusMonitor.add_watch() added watch for %s" % path_to_be_watched
                    # End debugging code
                
                # Note that we don't have to set invalidate to True here to 
                # bypass the cache because since there isn't one it will be
                # bypassed anyways. We could add it for clarity though.
                self.status(path)
        
    def status(self, path, invalidate=False):
        """
        
        This function doesn't return anything but calls the callback supplied
        to C{StatusMonitor} by the caller.
        
        UML sequence diagram depicting the status checks::
        
            +-----------------+                  +-------------+
            |  StatusMonitor  |                  |  VCSClient  |
            +-----------------+                  +-------------+
                    |                                   |
                    |    status(path, depth=empty)      |
                    |---------------------------------->|
                    |+-------------------+-------------+|
                    || [if isdir(path)]  |             ||
                    |+-------------------+             ||
                    ||                                 ||
                    ||          status(path)           ||
                    ||-------------------------------->||
                    |+---------------------------------+|
                    |                                   |
                    |+--------------------------+------+|
                    || [foreach parent folder]  |      ||
                    |+--------------------------+      ||
                    ||                                 ||
                    ||          status(path)           ||
                    ||-------------------------------->||
                    |+---------------------------------+|
                    |                                   |
        
        @type   path: string
        @param  path: The path for which to check the status.
        
        @type   invalidate: boolean
        @param  invalidate: Whether or not the cache should be bypassed.
        """
        
        # If we're not a or inside a working copy we don't even have to bother.
        if not self.vcs_client.is_in_a_or_a_working_copy(path): return
        
        # Begin debugging information
        print "Debug: StatusMonitor.status() called for %s" % path
        # End debugging information
        
        # We need the status object for the item alone
        # MARKER: performance 
        status = self.vcs_client.status_with_cache(
            path, 
            invalidate=invalidate, 
            depth=pysvn.depth.empty)[-1].data["text_status"]
            
        # A directory should have a modified status when any of its children
        # have a certain status (see modified_statuses below). Jason thought up 
        # of a nifty way to do this by using sets and the bitwise AND operator (&).
        if isdir(path) and status != pysvn.wc_status_kind.added:
            modified_statuses = set([
                pysvn.wc_status_kind.added, 
                pysvn.wc_status_kind.deleted, 
                pysvn.wc_status_kind.modified
            ])
            
            # MARKER: performance 
            sub_statuses = self.vcs_client.status_with_cache(path, invalidate=invalidate)[:-1]
            statuses = set([sub_status.data["text_status"] for sub_status in sub_statuses])
            
            if len(modified_statuses & statuses): 
                self.callback(path, "modified")
                
                #
                # We have to change the emblems on any parent directories aswell
                # when an item is modified this is pretty easy because we know
                # the status for the parent has to be "modified" too.
                #
                # There's another section below which also takes into account
                # the other statuses.
                #
                while path != "":
                    path = split_path(path)
                    if self.vcs_client.is_in_a_or_a_working_copy(path):
                        self.callback(path, "modified")
                        break;
                return;
        
        # Verifiying the rest of the statuses is common for both files and directories.
        if status in self.STATUS:
            self.callback(path, self.STATUS[status])
            
            # Now we have to invalidate the parent directories
            while path != "":
                path = split_path(path)
                if not self.vcs_client.is_in_a_or_a_working_copy(path): return
                    
                if status in (
                    pysvn.wc_status_kind.added, 
                    pysvn.wc_status_kind.deleted, 
                    pysvn.wc_status_kind.modified,
                ):
                    if not self.vcs_client.is_added(path): # FIXME: we should probably bypass the cache here
                        self.callback(path, "modified")
                elif status in (
                        pysvn.wc_status_kind.normal,
                        pysvn.wc_status_kind.unversioned, # FIXME: but only if it was previously versioned
                    ):
                    
                    # MARKER: performance 
                    self.status(path, invalidate=invalidate)
                    
                    # If we don't break out here it would result in the 
                    # recursive status checks on (^):
                    #
                    # /foo/bar/baz/qux
                    #   ^   ^   ^
                    #   ^   ^
                    #   ^
                    #
                    # Instead of "just":
                    #
                    # /foo/bar/baz/qux
                    #   ^   ^   ^
                    #
                    
                    # FIXME: if those were just cache hits performance would
                    # be significantly increased.
                    break;
