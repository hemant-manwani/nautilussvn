#==============================================================================
"""                             NautilusSvn

    This is an extension to the Nautilus file manager to allow better 
    integration with the Subversion source control system.

    Copyright Jason Field 2006

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
"""
                        TODO
                        ----

    1. Show conflicted files in dir diff
    2. Add Import function
    3. Add gnome properties integration
    4. Sort out commit status etc.

"""
#==============================================================================

__version__ = "0.11-1"

import copy
import glob
import gnomevfs
import gobject
import gtk
import nautilus
import os
import pysvn
import shutil
import sys
import time
import socket
import select
import pickle

# NautilusSvn is actually more than just this module so we need to add the entire
# directory to the path to be able to find our other modules. Because on import
# Python generates compiled (.pyc) versions of Python source code files we have
# to strip the 'c' from the extension to find the actual file.
sys.path.append(os.path.dirname(os.path.realpath(__file__.rstrip("c"))))

# FIXME: this (and other) should be moved into a nautilussvn module to prevent 
# collisions with other modules on the path.
from helper import *

def CheckForScanner():
    """ Checks whether our scanner process exists. If not, it launches it. """

    # Check if the scanner process exists
    files = glob.glob("/proc/*/cmdline")
    found = False
    for f in files:
        if "scanner.py" in file(f).read():
            found = True
            break

    # Start up the scanner since it isn't currently running
    if not found:
        return os.spawnl( os.P_NOWAIT, "/usr/bin/python", "python", GetPath("scanner.py") )
    else:
        return True

#============================================================================== 

class NautilusSvn(nautilus.InfoProvider, nautilus.MenuProvider, nautilus.ColumnProvider):
    """ This is the main class that implements all of our awesome features.
    """
    EMBLEMS = {
        "added" : 'svnadded',
        "deleted": 'svnremoved',
        "modified": 'svnmodified',
        "conflicted": 'svnconflict',
        "normal": "svncontrolled",
    }

    #-------------------------------------------------------------------------- 
    def __init__(self):
        """ Constructor - initialise our required storage
        """

        # This list keeps track of any files we have come across that will
        # need to be re-scanned if there is a commit/revert.
        self.monitoredFiles = []

        # This list keeps a record of all of the files we're planning to scan
        # when we get some idle time
        self.scanStack = []

        self.scan_in_progress = False

        self._socket = None

        CheckForScanner()

    #--------------------------------------------------------------------------
    def OnIdle(self):
        """ We use the idle handler to pop items from our scan stack and run a
            status scan on them. We do this so that we don't hog the processor
            each time a folder is opened.
        """
    
        # Check the socket connection to our scanner process
        if not self._socket:
            # There is no point carrying on with idle callbacks if there are no
            # items to scan
            if not len( self.scanStack ):
                return False

            # No connection, so see if we can connect
            try:
                self._socket = socket.socket()
                self._socket.connect( ( "", 33333 ) )
                self._socket.setblocking( 0 )
            except socket.error:
                # Can't connect to the socket - see if we need to start up the
                # scanner.
                self._socket = None
                return CheckForScanner()

            # The socket should be OK by now. We can grab an item from it and
            # send it to be processed.
            target = self.scanStack.pop()
            path = gnomevfs.get_local_path_from_uri( target.get_uri() )
            self._file_in_progress = target

            self._socket.send( path + "\n" )
            return True
        else:
            # We already have a connection, so we must be waiting for the
            # results of a scan. Check to see if it's available
            try:
                data = self._socket.recv( 8096 )
            except socket.error:
                return True

            # The data is available, so we can try to unpickle it
            try:
                data = pickle.loads( data )
            except EOFError:
                return len( self.scanStack ) > 0

            # Check if we need to act based on our data
            if data["status"]:

                file = self._file_in_progress

                # Now we need to update the file with the generated data
                if ENABLE_ATTRIBUTES:
                    if data["revision"]:
                        file.add_string_attribute('revision', str( data["revision"] ))
                    if data["author"]:
                        file.add_string_attribute('user', data["author"])

                # Update the display emblems if we're supposed to
                if ENABLE_EMBLEMS:
                    file.add_emblem( self.EMBLEMS[ data["status"] ] )

            # We're done with the socket
            self._socket = None

            # Get more callbacks if we have more items to scan
            return len( self.scanStack ) > 0

    #-------------------------------------------------------------------------- 
    def get_columns(self):
        """ This is the function called by Nautilus to find out what extra
            columns we can supply to it.
        """
        return (nautilus.Column("NautilusPython::revision_column",
                               "revision",
                               "Revision",
                               "The file revision"),
                nautilus.Column("NautilusPython::user_column",
                               "user",
                               "SVN User",
                               "The SVN user")

                )

    #-------------------------------------------------------------------------- 
    def update_file_info (self, file):
        """ Callback from Nautilus to get the file status.
        """

        if file.get_uri_scheme() != 'file':
            return

        # We'll scan the files during idle time, so add it to our stack
        self.scanStack.append(file)

        # If this is the first entry in an empty stack then we need to 
        # start idle callbacks
        if len(self.scanStack) == 1:
            gobject.idle_add(self.OnIdle)

    #-------------------------------------------------------------------------- 
    def get_file_items(self, window, files):
        """ Menu activated with files selected
        """

        # At the moment we're only handling single files or folders
        if len(files) < 1:
            return

        file = files[0]

        path = gnomevfs.get_local_path_from_uri(file.get_uri())

        items = [ ('NautilusPython::svndelete_file_item', 'SVN Delete' , 'Remove files from the repository.', self.OnDelete),
                  ('NautilusPython::svnrefreshstatus_file_item', 'SVN Refresh Status', 'Refresh the display status of the selected files.', self.OnRefreshStatus),
            ]

        if len( files ) == 1:
            items += [  ('NautilusPython::svnlog_file_item', 'SVN Log' , 'Log of %s' % file.get_name(), self.OnShowLog),
                        ('NautilusPython::svnupdate_file_item', 'SVN Update' , 'Get the latest code from the repository.', self.OnUpdate),
                        ('NautilusPython::svnproperties_file_item', 'SVN Properties', 'File properties for %s.'%file.get_name(), self.OnProperties), ]

        # Check if this is a folder, and if so if it's under source control
        if os.path.isdir(path):
            # Check if this folder is versioned
            if os.path.isdir(os.path.join(path, ".svn")):
                # Check if any of our children are modified.
                c = pysvn.Client()
                st = c.status(path, recurse=RECURSIVE_STATUS)
                statuses = set([x.text_status for x in st])
                t = set([   pysvn.wc_status_kind.modified,
                            pysvn.wc_status_kind.added,
                            pysvn.wc_status_kind.deleted])
                if len( t & statuses ):
                    # If so, add some useful menu items
                    items += [  ('NautilusPython::svndiffdir_file_item', 'SVN Diff' , 'Diff %s against the repository version' % file.get_name(), self.OnShowDiffDir),
                                ('NautilusPython::svncommit_file_item', 'SVN Commit' , 'Commit %s to the repository.' % file.get_name(), self.OnCommit),
                                ('NautilusPython::svnrevert_file_item', 'SVN Revert' , 'Revert %s back to the repository version.'%file.get_name(), self.OnRevert),]
            else:
                # Check if the parent is under source control
                if os.path.isdir(os.path.join(os.path.split(path)[0], ".svn")):
                    items = [('NautilusPython::svnadd_file_item', 'SVN Add' , 'Add %s to the repository.'%file.get_name(), self.OnAdd)]
                else:
                    return
        else:
            # We're a file, so lets check if we're in a versioned folder
            if os.path.isdir(os.path.join(os.path.split(path)[0], ".svn")):
                # OK we're in a versioned folder - are we already in SVN?
                c = pysvn.Client()
                st = c.status(path)[0]
                if not st.is_versioned:
                    # If not, we can only offer to add the file.
                    items = [('NautilusPython::svnadd_file_item', 'SVN Add' , 'Add %s to the repository.'%file.get_name(), self.OnAdd)]

                # Add the revert and diff items if we've changed from the repos version
                if st.text_status in [pysvn.wc_status_kind.added, pysvn.wc_status_kind.modified]:
                    items += [  ('NautilusPython::svnrevert_file_item', 'SVN Revert' , 'Revert %s back to the repository version.'%file.get_name(), self.OnRevert), ]

                    if len(files) == 1:
                        items += [  ('NautilusPython::svncommit_file_item', 'SVN Commit' , 'Commit %s to the repository.' % file.get_name(), self.OnCommit),
                                    ('NautilusPython::svndiff_file_item', 'SVN Diff' , 'Diff %s against the repository version' % file.get_name(), self.OnShowDiff),]

                # Add the conflict resolution menu items
                if st.text_status in [pysvn.wc_status_kind.conflicted]:
                    items += [  ('NautilusPython::svnrevert_file_item', 'SVN Revert' , 'Revert %s back to the repository version.'%file.get_name(), self.OnRevert), ]

                    if len(files) == 1:
                        items += [  ('NautilusPython::svneditconflict_file_item', 'SVN Edit Conflicts' , 'Edit the conflicts found when updating %s.'%file.get_name(), self.OnEditConflicts),
                                    ('NautilusPython::svnresolveconflict_file_item', 'SVN Conflicts Resolved' , 'Mark %s as resolved.'%file.get_name(), self.OnResolveConflicts), ]
            else:
                items = []

        # We now have a list of menu items to add - we can format the return in
        # a way that the Nautilus extensions understand
        itemlist = []
        for item in items:
            i = nautilus.MenuItem( item[0], item[1], item[2] )
            i.connect( 'activate', item[3], files )
            itemlist.append( i )

        return itemlist

    #-------------------------------------------------------------------------- 
    def get_background_items(self, window, file):
        """ Menu activated on window background
        """

        path = gnomevfs.get_local_path_from_uri(file.get_uri())

        if not os.path.isdir(os.path.join(path,".svn")):
            items = [   ('NautilusPython::svncheckout_file_item', 'SVN Checkout' , 'Checkout code from an SVN repository', self.OnCheckout)
                    ]
        else:
            items = [   ('NautilusPython::svnlog_file_item', 'SVN Log' , 'SVN Log of %s' % file.get_name(), self.OnShowLog),
                        ('NautilusPython::svncommit_file_item', 'SVN Commit' , 'Commit %s back to the repository.' % file.get_name(), self.OnCommit),
                        ('NautilusPython::svnupdate_file_item', 'SVN Update' , 'Get the latest code from the repository.', self.OnUpdate),
                        ('NautilusPython::svndiffdir_file_item', 'SVN Diff' , 'Diff %s against the repository version' % file.get_name(), self.OnShowDiffDir),
                        ('NautilusPython::svnrefreshstatus_file_item', 'SVN Refresh Status', 'Refresh the display status of %s.'%file.get_name(), self.OnRefreshStatus)
                    ]
        
        itemlist = []
        for item in items:
            i = nautilus.MenuItem(item[0], item[1], item[2])
            i.connect('activate', item[3], [file])
            itemlist.append(i)

        return itemlist

    #--------------------------------------------------------------------------
    def OnEditConflicts(self, menuitem, files):
        """ Edit Conflicts menu handler.
        """
        file = files[0] 

        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        revs = glob.glob(path + ".r*")
        revs.sort()
        revs.reverse()
        CallDiffTool(path + ".mine", path, revs[0])

    #-------------------------------------------------------------------------- 
    def OnResolveConflicts(self, menuitem, files):
        """ Resolve Conflicts menu handler.
        """
        file = files[0]
        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        c = pysvn.Client()
        c.resolved(path)
        file.invalidate_extension_info()

    #--------------------------------------------------------------------------
    def OnRevert(self, menuitem, files):
        """ Revert menu handler.
        """

        paths = [ gnomevfs.get_local_path_from_uri(file.get_uri()) for file in files ]

        dlg = gtk.MessageDialog(buttons=gtk.BUTTONS_YES_NO)
        dlg.set_markup("Are you sure you want to revert the following files?\n\n%s"%"\n".join(paths))

        if dlg.run() == gtk.RESPONSE_YES:
            c = pysvn.Client()
            for path in paths:
                c.revert(path, recurse=True)
            for file in files:
                file.invalidate_extension_info()
    
        dlg.destroy()

    #--------------------------------------------------------------------------
    def OnCheckout(self, menuitem, files):
        """ Checkout menu handler.
        """
        file = files[0]
        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnCheckout.py"), '%s' % path)

    #--------------------------------------------------------------------------
    def OnShowDiff(self, menuitem, files):
        """ Diff menu handler.
        """

        file = files[0]

        if not CheckDiffTool(): return

        path = gnomevfs.get_local_path_from_uri(file.get_uri())

        c = pysvn.Client()
        entry = c.info(path)
        
        df = os.popen('svn diff "%s"' % path).read()
        open("/tmp/tmp.patch", "w").write(df)
        shutil.copy(path, "/tmp")
        x = os.popen('patch --reverse "/tmp/%s" < /tmp/tmp.patch' % (os.path.split(path)[-1]))
        CallDiffTool(path, os.path.join("/tmp/", os.path.split(path)[-1]))

    #--------------------------------------------------------------------------
    def OnShowLog(self, menuitem, files):
        """ Show Log menu handler.
        """
        file = files[0]

        path = gnomevfs.get_local_path_from_uri(file.get_uri())

        os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnLog.py"), '%s' % path)

    #--------------------------------------------------------------------------
    def RescanFilesAfterProcess(self, pid):
        """ Rescans all of the files on our *monitoredFiles* list after the
            process specified by *pid* completes.
        """
        # We need a function that can check the file status once the process has completed.
        def ThreadProc():
            # First we need to see if the commit process is still running
            if os.path.exists("/proc/" + str(pid)):
                # If so, check its status by reading the status file from /proc
                f = open("/proc/%d/status"%pid).readlines()
                # if it's a zombie process, then we can waitpid() on it to end the process
                if "zombie" in f[1]:
                    os.waitpid(pid, 0)

                # Return true to get another callback after the next timeout
                return True
            else:
                # The process has completed, so we now want to rescan the 
                # files we're monitoring to see if their status has changed. We
                # need to make a copy of monitoredFiles as the rescanning process
                # will affect it.
                checkList = copy.copy(self.monitoredFiles)
                while len(checkList):
                    checkList.pop().invalidate_extension_info()
                return False

        # Add our callback function on a 1 second timeout
        gobject.timeout_add(1000, ThreadProc)

    #-------------------------------------------------------------------------- 
    def OnCommit(self, menuitem, files):
        """ Commit menu handler.
        """
        file = files[0]

        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        c = pysvn.Client()

        # Start up our commit dialog and message window script.
        pid = os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnCommit.py"), '%s' %path)

        self.RescanFilesAfterProcess(pid)

    #--------------------------------------------------------------------------
    def OnUpdate(self, menuitem, files):
        """ Update menu handler.
        """
        file = files[0]
        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        pid = os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnUpdate.py"), '%s' % path)
        self.RescanFilesAfterProcess(pid)

    #--------------------------------------------------------------------------
    def OnAdd(self, menuitem, files):
        """ Add menu handler.
        """
        c = pysvn.Client()
        for file in files:
            path = gnomevfs.get_local_path_from_uri(file.get_uri())
            c.add(path)
            file.invalidate_extension_info()

    #-------------------------------------------------------------------------- 
    def OnDelete(self, menuitem, files):
        """ Delete menu handler.
        """
        c = pysvn.Client()
        for file in files:
            path = gnomevfs.get_local_path_from_uri(file.get_uri())
            try:
                c.remove(path)
            except pysvn.ClientError,e:
                dlg = gtk.MessageDialog(buttons=gtk.BUTTONS_OK)
                dlg.set_markup("Couldn't delete the file, since it has local modifications.\nPlease revert or commit first.\n\n%s"%path)
                dlg.run()
                dlg.destroy()

    #--------------------------------------------------------------------------
    def OnShowDiffDir(self, menuitem, files):
        """ Dir Diff menu handler.
        """
        file = files[0]
        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnDirDiff.py"), '%s' % path)
        
    #--------------------------------------------------------------------------
    def OnRefreshStatus(self, menuitem, files):
        """ Refresh status menu handler. Invalidates the status of all of the selected files.
        """
        for file in files:
            file.invalidate_extension_info()

    #--------------------------------------------------------------------------
    def OnProperties(self, menuitem, files):
        """ Properties menu handler.
        """
        file = files[0]
        path = gnomevfs.get_local_path_from_uri(file.get_uri())
        os.spawnl(os.P_NOWAIT, "/usr/bin/python", "python", GetPath("SvnProperties.py"), '%s' % path)

#============================================================================== 
