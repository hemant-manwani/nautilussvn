#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
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

import os
import re

import nautilussvn.ui.dialog
import nautilussvn.lib.settings

def get_home_folder():
    """ 
    Returns the location of the hidden folder we use in the home dir.
    This is used for storing things like previous commit messages and
    previously used repositories.
    
    @rtype string
    @return The location of our main user storage folder
    
    """
    
    returner = os.path.abspath(
        os.path.expanduser("~/.nautilussvn")
    )
    if not os.path.exists(returner):
        os.mkdir(returner)

    return returner
    
def get_user_path():
    """
    Returns the location of the user's home directory.
    /home/$USER
    
    @rtype string
    @return The location of the user's home directory
    
    """
    
    return os.path.abspath(os.path.expanduser("~"))

def get_repository_paths_path():
    """
    Returns a valid URI for the repository paths file
    
    @rtype string
    @return the location of the repository paths file
    
    """
    return os.path.join(get_home_folder(), "repos_paths")

def get_repository_paths():
    """
    Gets all previous repository paths stored in the user's home folder
    
    @rtype list
    @return a list of previously used repository paths
    
    """
    
    returner = []
    paths_file = get_repository_paths_path()
    if os.path.exists(paths_file):
        returner = [x.strip() for x in open(paths_file, "r").readlines()]
        
    return returner

def get_previous_messages_path():
    """
    Returns a valid URI for the previous messages file
    
    @rtype string
    @returner the location of the previous messages file
    
    """
    
    return os.path.join(get_home_folder(), "previous_log_messages")

def get_previous_messages():
    """
    Gets all previous messages stored in the user's home folder
    
    @rtype list
    @return a list of previous used messages
    
    """
    
    path = get_previous_messages_path()
    if not os.path.exists(path):
        dlg = gtk.Dialog(
            "NautilusSvn", 
            "There are no previous messages to view", 
            [gtk.STOCK_OK, gtk.OK_RESPONSE]
        )
        dlg.run()
        dlg.destroy()
        return
        
    lines = open(path, "r").readlines()

    cur_entry = ""
    returner = []
    date = None
    msg = ""
    for line in lines:
        m = re.compile(r"-- ([\d:]+ [\d\.]+) --").match(line)
        if m:
            cur_entry = m.groups()[0]
            if date:
                returner.append((date, msg.replace("\n", "")))
                msg = ""
            date = cur_entry
        else:
            msg += line

    returner.reverse()
    
    return returner

def encode_revisions(revision_array):
    """
    Takes a list of integer revision numbers and converts to a TortoiseSVN-like
    format. This means we have to determine what numbers are consecutives and
    collapse them into a single element (see doctest below for an example).
    
    @type revision_array list of integers
    @param revision_array A list of revision numbers.
    
    @rtype string
    @return A string of revision numbers in TortoiseSVN-like format.
    
    >>> encode_revisions([4,5,7,9,10,11,12])
    '4-5,7,9-12'
    
    >>> encode_revisions([])
    ''
    
    >>> encode_revisions([1])
    '1'
    """
    
    # Let's get a couple of cases out of the way
    if len(revision_array) == 0:
        return ""
        
    if len(revision_array) == 1:
        return str(revision_array[0])
    
    # Instead of repeating a set of statements we'll just define them as an 
    # inner function.
    def append(start, last, list):
        if start == last:
            result = "%s" % start
        else: 
            result = "%s-%s" % (start, last)
            
        list.append(result)
    
    # We need a couple of variables outside of the loop
    start = revision_array[0]
    last = revision_array[0]
    current_position = 0
    returner = []
    
    while True:
        if current_position + 1 >= len(revision_array):
            append(start, last, returner)
            break;
        
        current = revision_array[current_position]
        next = revision_array[current_position + 1]
        
        if not current + 1 == next:
            append(start, last, returner)
            start = next
            last = next
        
        last = next
        current_position += 1
        
    return ",".join(returner)

def decode_revisions(string, head):
    """
    Takes a TortoiseSVN-like revision string and returns a list of integers.
    EX. 4-5,7,9-12 -> [4,5,7,9,10,11,12]
    
    Note: This function is a first draft.  It may not be production-worthy.
    """
    returner = []
    arr = string.split(",")
    for el in arr:
        if el.find("-") != -1:
            subarr = el.split("-")
            if subarr[1] == 'HEAD':
                subarr[1] = head
            for subel in range(int(subarr[0]), int(subarr[1])+1):
                returner.append(subel)
        else:
            returner.append(int(el))
            
    return returner

def get_diff_tool():
    """
    Gets the path to the diff_tool, and whether or not to swap lhs/rhs
    
    @rtype dict
    @return a dictionary with the diff tool path and swap boolean value
    """
    
    sm = nautilussvn.lib.settings.SettingsManager()
    diff_tool = sm.get("external", "diff_tool")
    diff_tool_swap = sm.get("external", "diff_tool_swap")
    
    return {
        "path": diff_tool, 
        "swap": diff_tool_swap
    }
    
def launch_diff_tool(lhs, rhs):
    """
    Launches the diff tool of choice
    
    @type lhs:  string
    @param lhs: the left hand side path
    
    @type rhs:  string
    @param lhs: the right hand side path
    """
    
    diff = get_diff_tool()
    
    if diff["path"] == "":
        return
    
    if not os.path.exists(diff["path"]):
        nautilussvn.ui.dialog.MessageBox("The diff tool %s was not found on your system.  Please either install this application or update your settings.")
        return
        
    if diff["swap"]:
        (lhs, rhs) = (rhs, lhs)
    
    os.spawnl(
        os.P_NOWAIT,
        diff["path"],
        diff["path"],
        lhs,
        rhs
    )
    
def get_file_extension(path):
    """
    Wrapper that retrieves a file path's extension
    
    @type   path: string
    @param  path: a filename or path
    
    @rtype  string
    @return a file extension
    
    """
    
    return os.path.splitext(path)[1]
    
def open_item(path):
    """
    Use GNOME default opener to handle file opening
    
    @type   path: string
    @param  path: a file path
    
    """
    
    if path == "" or path is None:
        return
    
    os.system("gnome-open %s" % path)
    
def browse_to_item(path):
    """
    Browse to the specified path in the file manager
    
    @type   path: string
    @param  path: a file path
    
    """

    os.system("nautilus --no-desktop --browser %s" % os.path.dirname(path))
