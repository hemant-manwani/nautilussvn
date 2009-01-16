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
  
"""

import os.path
from os.path import isdir, isfile

import gnomevfs
import nautilus
import pysvn
import gobject
import gtk

from nautilussvn.lib.vcs import create_vcs_instance
from nautilussvn.lib.vcs.svn import SVN

import nautilussvn.lib.dbus.service
from nautilussvn.lib.dbus.status_monitor import StatusMonitorStub as StatusMonitor
from nautilussvn.lib.dbus.svn_client import SVNClientStub as SVNClient

from nautilussvn.lib.helper import split_path, launch_ui_window, launch_diff_tool, get_file_extension
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
        # Start up our DBus service if it's not already started, if this fails
        # we can't really do anything.
        self.dbus_service_available = nautilussvn.lib.dbus.service.start()
            
        # Create a StatusMonitor and register a callback with it to notify us 
        # of any status changes.
        if self.dbus_service_available:
            self.status_monitor = StatusMonitor(self.cb_status)
        else:
            # Might aswell fallback on our non DBus status monitor
            from nautilussvn.lib.vcs.svn import StatusMonitor as LocalStatusMonitor
            self.status_monitor = LocalStatusMonitor(self.cb_status)
        
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
        
        vcs_client = SVNClient()
        has_watch = self.status_monitor.has_watch(path)
        is_in_a_or_a_working_copy = vcs_client.is_in_a_or_a_working_copy(path)
        
        if not has_watch and is_in_a_or_a_working_copy:
            self.status_monitor.add_watch(path)
            self.status_monitor.status(path)
            
        # If we access the StatusMonitor over DBus it keeps running even though 
        # Nautilus is not. So watches will stay attached. So an initial status 
        # check won't be done. Though there are other situations where there is
        # a watch but we don't have a status yet.
        if (has_watch and
                not path in self.statuses and
                is_in_a_or_a_working_copy):
            self.status_monitor.status(path)
        
    def get_file_items(self, window, items):
        """
        Menu activated with items selected. Nautilus also calls this function
        when rendering submenus, even though this is not needed since the entire
        menu has already been returned.
        
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
        
        self.nautilusVFSFile_table[path] = item
        
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
        
        # See comment for variable: statuses
        # There's no reason to do a lot of stuff if the emblem is the same
        # but since we're the only function who does a add_emblem, we have to.
        # We might not have a NautilusVFSFile yet but we can already store the
        # status.
        self.statuses[path] = status
        
        if not path in self.nautilusVFSFile_table: return
        item = self.nautilusVFSFile_table[path]
        
        # We need to invalidate the extension info for only one reason:
        #
        # - Invalidating the extension info will cause Nautilus to remove all
        #   temporary emblems we applied so we don't have overlay problems
        #   (with ourselves, we'd still have some with other extensions).
        #
        # After invalidating update_file_info applies the correct emblem.
        #
        item.invalidate_extension_info()
        
        # FIXME: for some reason when not using the DBus service C{update_file_info}
        # isn't always called, which doesn't make sense but ok.
        if not self.dbus_service_available:
            self.set_emblem_by_status(path, status)
    
class MainContextMenu():
    """
    
    A class that represents our context menu.
    
    See: http://code.google.com/p/nautilussvn/wiki/ContextMenuStructure
    
    FIXME: There's currently a problem with the order in which menu items 
    appear, even though a list such as C{[<Update>, <Commit>, <NautilusSvn>]} 
    would be returned it might end up as C{[<NautilusSvn>, <Update>, <Commit>]}.
    
    """
    
    SEPARATOR = "- - - - - - - - - - - - - - - - -"
    
    def __init__(self, paths, nautilussvn_extension):
        self.paths = paths
        self.nautilussvn_extension = nautilussvn_extension
        self.vcs_client = SVNClient()
        
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
                        "identifier": "NautilusSvn::DBus",
                        "label": "DBus",
                        "tooltip": "",
                        "icon": "nautilussvn-dbus",
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": (lambda: True),
                        "submenus": [
                            {
                                "identifier": "NautilusSvn::DBus_Restart",
                                "label": "Start/Restart Service",
                                "tooltip": "",
                                "icon": "nautilussvn-run",
                                "signals": {
                                    "activate": {
                                        "callback": self.callback_dbus_restart,
                                        "args": None
                                    }
                                }, 
                                "condition": (lambda: True),
                                "submenus": [
                                    
                                ]
                            },
                            {
                                "identifier": "NautilusSvn::DBus_Exit",
                                "label": "Exit Service",
                                "tooltip": "",
                                "icon": "nautilussvn-stop",
                                "signals": {
                                    "activate": {
                                        "callback": self.callback_dbus_exit,
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
                        "identifier": "NautilusSvn::Bugs",
                        "label": "Bugs",
                        "tooltip": "",
                        "icon": "nautilussvn-bug",
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
                            }
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
                                "args": None,
                                "kwargs": {"recurse": True}
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
                        "callback": self.callback_checkout,
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
                                "callback": self.callback_diff,
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
                                "callback": self.callback_show_log,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_show_log,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator1",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": (lambda: True),
                        "submenus": []
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
                        "identifier": "NautilusSvn::AddToIgnoreList",
                        "label": "Add to ignore list",
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": self.condition_add_to_ignore_list,
                        "submenus": [
                            {
                                "identifier": "NautilusSvn::AddToIgnoreFile",
                                "label": os.path.basename(self.paths[0]),
                                "tooltip": "",
                                "icon": None,
                                "signals": {
                                    "activate": {
                                        "callback": self.callback_ignore_filename,
                                        "args": None
                                    }
                                }, 
                                "condition": (lambda: True),
                                "submenus": [
                                ]
                            },
                            {
                                "identifier": "NautilusSvn::AddToIgnoreExt",
                                "label": "*.%s"%get_file_extension(self.paths[0]),
                                "tooltip": "",
                                "icon": None,
                                "signals": {
                                    "activate": {
                                        "callback": self.callback_ignore_ext,
                                        "args": None
                                    }
                                }, 
                                "condition": self.condition_ignore_ext,
                                "submenus": [
                                ]
                            }
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::UpdateToRevision",
                        "label": "Update to revision...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_updateto,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_updateto,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Rename",
                        "label": "Rename...",
                        "tooltip": "",
                        "icon": "nautilussvn-rename",
                        "signals": {
                            "activate": {
                                "callback": self.callback_rename,
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
                        "identifier": "NautilusSvn::Resolve",
                        "label": "Resolve",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_resolve,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_resolve,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::GetLock",
                        "label": "Get Lock...",
                        "tooltip": "",
                        "icon": "nautilussvn-lock",
                        "signals": {
                            "activate": {
                                "callback": self.callback_lock,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_lock,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator2",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": (lambda: True),
                        "submenus": []
                    },
                    {
                        "identifier": "NautilusSvn::Export",
                        "label": "Export",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_export,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_export,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Create",
                        "label": "Create repository here...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": None,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_create,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Import",
                        "label": "Import",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_import,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_import,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator3",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": (lambda: True),
                        "submenus": []
                    },
                    {
                        "identifier": "NautilusSvn::BranchTag",
                        "label": "Branch/tag...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_branch,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_branch,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Switch",
                        "label": "Switch...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_switch,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_switch,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Merge",
                        "label": "Merge...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_merge,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_merge,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator4",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": (lambda: True),
                        "submenus": []
                    },
                    {
                        "identifier": "NautilusSvn::Blame",
                        "label": "Blame...",
                        "tooltip": "",
                        "icon": None,
                        "signals": {
                            "activate": {
                                "callback": self.callback_blame,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_blame,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator5",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
                        "signals": {}, 
                        "condition": (lambda: True),
                        "submenus": []
                    },
                    {
                        "identifier": "NautilusSvn::Properties",
                        "label": "Properties",
                        "tooltip": "",
                        "icon": "nautilussvn-properties",
                        "signals": {
                            "activate": {
                                "callback": self.callback_properties,
                                "args": None
                            }
                        }, 
                        "condition": self.condition_properties,
                        "submenus": [
                            
                        ]
                    },
                    {
                        "identifier": "NautilusSvn::Separator6",
                        "label": self.SEPARATOR,
                        "tooltip": "",
                        "icon": None,
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
                        "condition": (lambda: False),
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
                                "callback": self.callback_settings,
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
                                "callback": self.callback_about,
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
                "condition": (lambda: True),
                "submenus": [
                    
                ]
            }
        
        @type   menu_definition:  list
        @param  menu_definition:  A list of definition items.
        
        @rtype:     list of MenuItems
        @return:    A list of MenuItems representing the context menu.
        
        """
        
        menu = []
        prevlabel = None
        is_first = True
        index = 0
        length = len(menu_definition)
        for definition_item in menu_definition:
            is_last = (index+1 == length)
            if definition_item["condition"]():

                # If the item is a separator, don't show it if this is the first
                # or last item, or if the previous item was a separator
                if (definition_item["label"] == self.SEPARATOR and
                        (is_first or is_last or prevlabel == self.SEPARATOR)):
                    index += 1
                    continue
            
                menu_item = nautilus.MenuItem(
                    definition_item["identifier"],
                    definition_item["label"],
                    definition_item["tooltip"],
                    definition_item["icon"]
                )
                
                for signal, value in definition_item["signals"].items():
                    if value["callback"] != None:
                        # FIXME: the adding of arguments need to be done properly
                        if "kwargs" in value:
                            menu_item.connect(signal, value["callback"], self.paths, value["kwargs"])    
                        else:
                            menu_item.connect(signal, value["callback"], self.paths)
                
                menu.append(menu_item)
                
                # The menu item above as just been added, so we can note that
                # we're no longer on the first menu item.  And we'll keep
                # track of this item so the next iteration can test if it should
                # show a separator or not
                is_first = False
                prevlabel = definition_item["label"]
                
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

            index += 1
            
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
                        self.vcs_client.is_deleted(path) or
                        not self.vcs_client.is_versioned(path)):
                    return True
                else:
                    if (isdir(path) and
                            (self.vcs_client.has_added(path) or 
                            self.vcs_client.has_modified(path) or
                            self.vcs_client.has_deleted(path)) or
                            self.vcs_client.has_unversioned(path)):
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
                    not self.vcs_client.is_versioned(path)):
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
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]) and
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
    
    def condition_add_to_ignore_list(self):
        return (len(self.paths) == 1 and 
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]) and
                not self.vcs_client.is_versioned(self.paths[0]))
    
    def condition_ignore_ext(self):
        return isfile(self.paths[0])

    def condition_lock(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
            
        return False

    def condition_branch(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
            
        return False

    def condition_switch(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
            
        return False

    def condition_merge(self):
        for path in self.paths:
            if (self.vcs_client.is_in_a_or_a_working_copy(path) and
                    self.vcs_client.is_versioned(path)):
                return True
            
        return False

    def condition_import(self):
        return (len(self.paths) == 1 and
                not self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]))

    def condition_export(self):
        return (len(self.paths) == 1 and
                not self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]))
    
    def condition_updateto(self):
        return (len(self.paths) == 1 and 
                self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]))
    
    def condition_resolve(self):
        # TODO: Implement has_conflicted/is_conflicted methods
        return False
    
    def condition_create(self):
        return (len(self.paths) == 1 and
                not self.vcs_client.is_in_a_or_a_working_copy(self.paths[0]))
    
    #
    # Callbacks
    #
    
    # Begin debugging callbacks
    def callback_dbus_restart(self, menu_item, path):
        import time
        if self.nautilussvn_extension.dbus_service_available:
            nautilussvn.lib.dbus.service.exit()
            time.sleep(1)
        else:
            nautilussvn.lib.dbus.service.start()
            
        self.nautilussvn_extension.dbus_service_available = (
            nautilussvn.lib.dbus.service.start())
        
        # All references to the previous DBus will now have been invaldated
        time.sleep(1)
        self.nautilussvn_extension.status_monitor = (
            StatusMonitor(self.nautilussvn_extension.cb_status))
        
    def callback_dbus_exit(self, menu_item, paths):
        nautilussvn.lib.dbus.service.exit()
        self.nautilussvn_extension.dbus_service_available = False
    
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
    
    def callback_refresh_status(self, menu_item, paths, recurse=False):
        """
        Refreshes an item status, so it will always bypass the cache.
        
        TODO:
        Add should only go downwards. Lower is added, up is modified. 
        Revert should go downwards. Check on highest folder?
        Commit should go downwards. Check on highest folder?
        Update should go downwards. Only conflicts matter?
        """
        
        nautilussvn_extension = self.nautilussvn_extension
        status_monitor = nautilussvn_extension.status_monitor
        for path in paths:
            status_monitor.status(path, invalidate=True)
    
    def callback_debug_revert(self, menu_item, paths):
        client = pysvn.Client()
        for path in paths:
            client.revert(path, recurse=True)
        
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

    def callback_checkout(self, menu_item, paths):
        launch_ui_window("checkout", paths[0])
    
    def callback_update(self, menu_item, paths):
        launch_ui_window("update", " ".join(paths))

    def callback_commit(self, menu_item, paths):
        launch_ui_window("commit", " ".join(paths))

    def callback_add(self, menu_item, paths):
        launch_ui_window("add", " ".join(paths))

    def callback_delete(self, menu_item, paths):
        # This really needs to go thgou
        client = pysvn.Client()
        for path in paths:
            # TODO: Abstract this away from pysvn
            client.remove(path, force=True)
        self.callback_refresh_status(menu_item, paths)

    def callback_revert(self, menu_item, paths):
        launch_ui_window("revert", " ".join(paths))

    def callback_diff(self, menu_item, paths):
        launch_diff_tool(paths[0])
    
    def callback_show_log(self, menu_item, paths):
        launch_ui_window("log", paths[0])

    def callback_rename(self, menu_item, paths):
        launch_ui_window("rename", paths[0])

    def callback_properties(self, menu_item, paths):
        launch_ui_window("properties", paths[0])

    def callback_about(self, menu_item, paths):
        launch_ui_window("about")
        
    def callback_settings(self, menu_item, paths):
        launch_ui_window("settings")
    
    def callback_ignore_filename(self, menu_item, paths):
        pass

    def callback_ignore_ext(self, menu_item, paths):
        pass

    def callback_lock(self, menu_item, paths):
        launch_ui_window("lock", " ".join(paths))

    def callback_branch(self, menu_item, paths):
        launch_ui_window("branch", paths[0])

    def callback_switch(self, menu_item, paths):
        launch_ui_window("switch", paths[0])

    def callback_merge(self, menu_item, paths):
        launch_ui_window("merge", paths[0])

    def callback_import(self, menu_item, paths):
        launch_ui_window("import", paths[0])

    def callback_export(self, menu_item, paths):
        launch_ui_window("export", paths[0])

    def callback_updateto(self, menu_item, paths):
        launch_ui_window("updateto", paths[0])
    
    def callback_resolve(self, menu_item, paths):
        launch_ui_window("resolve", " ".join(paths))
        
    def callback_blame(self, menu_item, paths):
        launch_ui_window("blame", paths[0])
