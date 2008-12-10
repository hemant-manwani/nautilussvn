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

from os.path import isdir, isfile

import gnomevfs
import nautilus
import pysvn

from nautilussvn.lib.vcs import VCSFactory

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ 
    This is the main class that implements all of our awesome features.
    
    """
    
    def __init__(self):
        pass
        
    def get_columns(self):
        """
        
        
        """
        
        pass
        
    def update_file_info(self, file):
        """
        Callback from Nautilus to get the file status. This is where the magic 
        happens! This function check the current status of *file*, and updates 
        the display with the relevant emblem.
        
        @type   file: NautilusVFSFile
        @param  file: 
        
        """
        
        # If we're not a or inside a working copy we don't even have to bother.
        
        
        # If we're a directory we have to do a recursive status check to see if
        # any files below us have modifications (added, modified or deleted).
        
        
        # Verifiying one of following statuses: 
        #   added, missing, deleted
        # is common for both single files and directories.
        
        
        pass
        
    def get_file_items(self, window, files):
        """
        Menu activated with files selected.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        
        @type   files: list of NautilusVFSFile
        @param  files:
        
        """
        
        return MainContextMenu(files).construct_menu()
        
    def get_background_items(self, window, file):
        """
        Menu activated on window background.
        
        @type   window: NautilusNavigationWindow
        @param  window:
        @type   file:   NautilusVFSFile
        @param  file:
        
        """
        
        return MainContextMenu([file]).construct_menu()
        
class MainContextMenu():
    """
    
    
    """
    
    def __init__(self, files):
        self.files = [
            gnomevfs.get_local_path_from_uri(file.get_uri()) for file in files
        ]
        self.vcs = VCSFactory().create_vcs_instance()
        
    def construct_menu(self):
        """
        
        """
        
        # The following dictionary defines the complete contextmenu, you can
        # refer to any future local variables using the syntax $var and ${var}.
        menu_definition = [
            {
                "identifier": "NautilusSvn::Checkout",
                "label": "Checkout",
                "tooltip": "Checkout code from an SVN repository",
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
        if (len(self.files) == 1 and 
                isdir(self.files[0]) and 
                not self.vcs.is_working_copy(self.files[0])):
            return True
        return False
        
    def condition_update(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and
                    self.vcs.is_versioned(file) and 
                    not self.vcs.is_added(file)):
                return True
        return False
        
    def condition_commit(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and
                    self.vcs.is_modified(file)):
                return True
        return False
        
    def condition_diff(self):
        for file in self.files:
            if (not isfile(file)):
                return False
        
        if (len(self.files) == 2):
            return True
            
        if (len(self.files) == 1 and
                self.vcs.is_working_copy(self.files[0]) and
                self.vcs.is_modified(self.files[0])):
            return True
        
        return False
        
    def condition_show_log(self):
        if (len(self.files) == 1 and 
                self.vcs.is_working_copy(self.files[0]) and
                not self.vcs.is_added(self.files[0])):
            return True
        return False
        
    def condition_add(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and
                not self.vcs.is_versioned(file)):
                return True
        return False
        
    def condition_add_to_ignore_list(self):
        pass
        
    def condition_rename(self):
        if (len(self.files) == 1 and 
                self.vcs.is_working_copy(self.files[0]) and
                self.vcs.is_versioned(self.files[0])):
            return True
        return False
        
    def condition_delete(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and
                    self.vcs.is_versioned(file)):
                return True
        return False
        
    def condition_revert(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and
                    (self.vcs.is_modified(file) or
                    self.vcs.is_added(file))):
                return True
        return False
        
    def condition_blame(self):
        if (len(self.files) == 1 and
                self.vcs.is_working_copy(self.files[0]) and
                self.vcs.is_versioned(self.files[0])):
            return True
        return False
        
    def condition_properties(self):
        for file in self.files:
            if (self.vcs.is_working_copy(file) and 
                    self.vcs.is_versioned(file)):
                return True
        return False


    
    
