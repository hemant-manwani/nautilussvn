"""

All sorts of helper functions.

"""

import locale
import os
import os.path
import subprocess
import re
import datetime
import time
import shutil

import nautilussvn
from nautilussvn.util.path import get_home_folder
from nautilussvn.util.locale import DATETIME_FORMAT

def launch_ui_window(filename, args=[]):
    """
    Launches a UI window in a new process, so that we don't have to worry about
    nautilus and threading.
    
    @type   filename:   string
    @param  filename:   The filename of the window, without the extension
    
    @type   args:       list
    @param  args:       A list of arguments to be passed to the window.
    
    @rtype:             integer
    @return:            The pid of the process (if launched)
    """
    
    # Construct a path to the actual python file
    basedir = os.path.dirname(os.path.realpath(nautilussvn.__file__))
    path = "%s/ui/%s.py" % (basedir, filename)
    
    if os.path.exists(path): 
        return subprocess.Popen(["/usr/bin/python", path] + args).pid
    else:
        return False

def get_user_path():
    """
    Returns the location of the user's home directory.
    /home/$USER
    
    @rtype:     string
    @return:    The location of the user's home directory.
    
    """
    
    return os.path.abspath(os.path.expanduser("~"))

def get_repository_paths_path():
    """
    Returns a valid URI for the repository paths file
    
    @rtype:     string
    @return:    The location of the repository paths file.
    
    """
    return os.path.join(get_home_folder(), "repos_paths")

def get_repository_paths():
    """
    Gets all previous repository paths stored in the user's home folder
    
    @rtype:     list
    @return:    A list of previously used repository paths.
    
    """
    
    returner = []
    paths_file = get_repository_paths_path()
    if os.path.exists(paths_file):
        returner = [x.strip() for x in open(paths_file, "r").readlines()]
        
    return returner

def get_previous_messages_path():
    """
    Returns a valid URI for the previous messages file
    
    @rtype:     string
    @return:    The location of the previous messages file.
    
    """
    
    return os.path.join(get_home_folder(), "previous_log_messages")

def get_previous_messages():
    """
    Gets all previous messages stored in the user's home folder
    
    @rtype:     list
    @return:    A list of previous used messages.
    
    """
    
    path = get_previous_messages_path()
    if not os.path.exists(path):
        return
        
    lines = open(path, "r").readlines()

    cur_entry = ""
    returner = []
    date = None
    msg = ""
    for line in lines:
        m = re.compile(r"-- ([\d\-]+ [\d\:]+) --").match(line)
        if m:
            cur_entry = m.groups()[0]
            if date:
                returner.append((date, msg.replace("\n", "")))
                msg = ""
            date = cur_entry
        else:
            msg += line

    if date and msg:
        returner.append((date, msg.replace("\n", "")))

    returner.reverse()
    
    return returner

def encode_revisions(revision_array):
    """
    Takes a list of integer revision numbers and converts to a TortoiseSVN-like
    format. This means we have to determine what numbers are consecutives and
    collapse them into a single element (see doctest below for an example).
    
    @type revision_array:   list of integers
    @param revision_array:  A list of revision numbers.
    
    @rtype:                 string
    @return                 A string of revision numbers in TortoiseSVN-like format.
    
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
    
    TODO: This function is a first draft.  It may not be production-worthy.
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
    Gets the path to the diff_tool, and whether or not to swap lhs/rhs.
    
    @rtype:     dictionary
    @return:    A dictionary with the diff tool path and swap boolean value.
    """
    
    sm = nautilussvn.util.settings.SettingsManager()
    diff_tool = sm.get("external", "diff_tool")
    diff_tool_swap = sm.get("external", "diff_tool_swap")
    
    return {
        "path": diff_tool, 
        "swap": diff_tool_swap
    }
    
def launch_diff_tool(path1, path2=None):
    """
    Launches the diff tool of choice.
    
      1.  Generate a standard diff between the path and the latest revision.
      2.  Write the diff text to a tmp file
      3.  Copy the given file (path) to the tmp directory
      4.  Do a reverse patch to get a version of the file that is in the repo.
      5.  Now you have two files and you can send them to the diff tool.
    
    @type   paths: list
    @param  paths: Paths to the given files

    """
    
    diff = get_diff_tool()
    
    if diff["path"] == "":
        return
    
    if not os.path.exists(diff["path"]):
        return

    # If path2 is set, that means we are comparing one file/folder to another
    if path2 is not None:
        (lhs, rhs) = (path1, path2)
    else:
        patch = os.popen("svn diff --diff-cmd 'diff' '%s'" % path1).read()
        open("/tmp/tmp.patch", "w").write(patch)
        
        tmp_path = "/tmp/%s" % os.path.split(path1)[-1]
        shutil.copy(path1, "/tmp")
        os.popen(
            "patch --reverse '%s' < /tmp/tmp.patch" % 
            tmp_path
        )
        (lhs, rhs) = (path1, tmp_path)
        
    if diff["swap"]:
        (lhs, rhs) = (rhs, lhs)
    
    os.spawnl(
        os.P_NOWAIT,
        diff["path"],
        diff["path"],
        lhs,
        rhs
    )
    
def open_item(path):
    """
    Use GNOME default opener to handle file opening.
    
    @type   path: string
    @param  path: A file path.
    
    """
    
    if path == "" or path is None:
        return
    
    subprocess.Popen(["gnome-open", os.path.abspath(path)])
    
def browse_to_item(path):
    """
    Browse to the specified path in the file manager
    
    @type   path: string
    @param  path: A file path.
    
    """

    subprocess.Popen([
        "nautilus", "--no-desktop", "--browser", 
        os.path.dirname(os.path.abspath(path))
    ])
    
def delete_item(path):
    """
    Send an item to the trash. 
    
    @type   path: string
    @param  path: A file path.
    """

    subprocess.Popen(["gvfs-trash", os.path.abspath(path)]).pid
    
def save_log_message(message):
    """
    Saves a log message to the user's home folder for later usage
    
    @type   message: string
    @param  message: A log message.
    
    """
    
    messages = []
    path = get_previous_messages_path()
    if os.path.exists(path):
        limit = get_log_messages_limit()
        messages = get_previous_messages()

        # If the current message already exists, delete the old one
        # The new one will take it's place at the top
        tmp = []
        for i, m in enumerate(messages):
            if message != m[1]:
                tmp.append(m)
        
        messages = tmp
             
        # Don't allow the number of messages to pile up past the limit
        while len(messages) > limit:
            messages.pop()

    t = time.strftime(DATETIME_FORMAT)
    messages.insert(0, (t, message))    
    
    f = open(get_previous_messages_path(), "w")
    s = ""
    for m in messages:
        s = """\
-- %s --
%s
%s
"""%(m[0], m[1], s)

    f.write(s.encode("utf-8"))
    f.close()

def save_repository_path(path):
    """
    Saves a repository path to the user's home folder for later usage
    If the given path has already been saved, remove the old one from the list
    and append the new one to the end.
    
    @type   path: string
    @param  path: A repository path.
    
    """
    
    paths = get_repository_paths()
    if path in paths:
        paths.pop(paths.index(path))
    paths.insert(0, path)
    
    limit = get_repository_paths_limit()
    while len(paths) > limit:
        paths.pop()
    
    f = open(get_repository_paths_path(), "w")
    f.write("\n".join(paths).encode("utf-8"))
    f.close()
    
def get_log_messages_limit():
    sm = nautilussvn.util.settings.SettingsManager()
    return int(sm.get("cache", "number_messages"))

def get_repository_paths_limit():
    sm = nautilussvn.util.settings.SettingsManager()
    return int(sm.get("cache", "number_repositories"))
    
def pretty_timedelta(time1, time2, resolution=None):
    """
    Calculate time delta between two C{datetime} objects.
    (the result is somewhat imprecise, only use for prettyprinting).
    
    Was originally based on the function pretty_timedelta from:
	http://trac.edgewall.org/browser/trunk/trac/util/datefmt.py
    """
    
    if time1 > time2:
        time2, time1 = time1, time2
    diff = time2 - time1
    age_s = int(diff.days * 86400 + diff.seconds)
    if resolution and age_s < resolution:
        return ""
    
    # I do not see a way to make this less repetitive - to make the 
    # strings fully translatable (i.e. also for languages that have more
    # or less than two plural forms) we have to state all the strings
    # explicitely within an ngettext call
    if age_s <= 60 * 1.9:
        return ngettext("%i second", "%i seconds",age_s) % age_s
    elif age_s <= 3600 * 1.9:
        r = age_s / 60
        return ngettext("%i minute", "%i minutes",r) % r
    elif age_s <= 3600 * 24 * 1.9:
        r = age_s / 3600
        return ngettext("%i hour", "%i hours",r) % r        		
    elif age_s <= 3600 * 24 * 7 * 1.9:
        r = age_s / (3600 * 24)
        return ngettext("%i day", "%i days",r) % r
    elif age_s <= 3600 * 24 * 30 * 1.9:
        r = age_s / (3600 * 24 * 7)
        return ngettext("%i week", "%i weeks",r) % r
    elif age_s <= 3600 * 24 * 365 * 1.9:
        r = age_s / (3600 * 24 * 30)
        return ngettext("%i month", "%i months",r) % r
    else:
        r = age_s / (3600 * 24 * 365)
        return ngettext("%i year", "%i years",r) % r        

def _commonpath(l1, l2, common=[]):
    """
    Helper method for the get_relative_path method
    """
    if len(l1) < 1: return (common, l1, l2)
    if len(l2) < 1: return (common, l1, l2)
    if l1[0] != l2[0]: return (common, l1, l2)
    return _commonpath(l1[1:], l2[1:], common+[l1[0]])
    
def get_relative_path(p1, p2):
    """
    Method that returns the relative path between the specified paths
    """
    (common,l1,l2) = _commonpath(p1.split(os.path.sep), p2.split(os.path.sep))
    p = []
    if len(l1) > 0:
        p = [ '../' * len(l1) ]
    p = p + l2
    return os.path.join( *p )
