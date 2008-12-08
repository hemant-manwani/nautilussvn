#==============================================================================
""" Copyright Jason Field 2006

    This file is part of NautilusSvn.

    NautilusSvn is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    NautilusSvn is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with NautilusSvn; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
#==============================================================================

import os
import re

# Set to True to add emblems to version controlled files showing their status
ENABLE_EMBLEMS = True

# Set to True to add author and revision attributes to files, which are then
# visible via columns in Nautilus
ENABLE_ATTRIBUTES = True

# Tool that should be used for diffs
DIFF_TOOL = "meld"

# The path to the folder containing all of our source files.
SOURCE_PATH = os.path.dirname(os.path.realpath(__file__.rstrip("c")))

# Set to True to enable recursive status checks. This might be slow when using
# a remote repository over a slow connection.
RECURSIVE_STATUS = True

# Set to True to swap the order of old and new versions of files in diff tool
# Default is False, new version at left and old one at right
SWAP = False

#==============================================================================

# A useful macro that's used all over the shop.
def GetPath(path):
    """ This function is a helper for the other files so that they can find the
        resource files etc. that they require.
    """
    return os.path.join(SOURCE_PATH, path)

def GetHomeFolder():
    """ Returns the location of the hidden folder we use in the home dir.
        This is used for storing things like previous commit messages and
        previously used repositories.
    """
    fldr = os.path.abspath( os.path.expanduser("~/.nautilussvn") )
    if not os.path.exists( fldr ):
        os.mkdir( fldr )
    return fldr

# Checks that the defined diff tool exists. If not, let the user know.
def CheckDiffTool():
    if not os.path.exists(os.path.join("/usr/bin", DIFF_TOOL)):
        
        import gtk
        dlg = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)

        msg = "The diff tool set in %s does not exist.\n\nEither install %s, or update helper.py to point to the correct tool you'd like to use.."%(GetPath("helper.py"),DIFF_TOOL)
        dlg.set_markup(msg)
        def OnResponse(widget, event):
            dlg.destroy()
        dlg.connect("response", OnResponse)
        dlg.set_property("title", "NautilusSvn")
        dlg.run()
        return False
    else:
        return True

def CallDiffTool(lhs, rhs, rev=-1):
    if SWAP:   (lhs, rhs) = (rhs, lhs)
    if rev == -1:
        os.spawnl(os.P_NOWAIT, os.path.join("/usr/bin/", DIFF_TOOL), DIFF_TOOL, lhs, rhs)
    else:
        os.spawnl(os.P_NOWAIT, os.path.join("/usr/bin/", DIFF_TOOL), DIFF_TOOL, lhs, rhs, rev)

def GetRepositoryPaths():
    paths_file = os.path.join( GetHomeFolder(), "repos_paths" )
    paths = [] # just to make sure there is at least a property set
    if os.path.exists(paths_file):
        paths = [x.strip() for x in open(paths_file, "r").readlines()]
    return paths

def GetPreviousMessages():
    plm = os.path.join( GetHomeFolder(), "previous_log_messages" )
    if not os.path.exists( plm ):
        dlg = gtk.Dialog("NautilusSvn", "There are no previous messages to view", [gtk.STOCK_OK, gtk.OK_RESPONSE])
        dlg.run()
        dlg.destroy()
        return
        
    lines = open( plm, "r" ).readlines()

    # Grab all of the entries
    cur_entry = ""
    entries = []
    date = None
    msg = ""
    for line in lines:
        m = re.compile(r"-- ([\d:]+ [\d\.]+) --").match(line)
        if m:
            cur_entry = m.groups()[0]
            if date:
                entries.append( (date, msg.replace("\n", "")) )
                msg = ""
            date = cur_entry
        else:
            msg += line

    entries.reverse()
    
    return entries


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

