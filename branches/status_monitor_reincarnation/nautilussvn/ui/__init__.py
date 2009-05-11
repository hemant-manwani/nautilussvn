import os.path
import subprocess

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
    basedir = os.path.dirname(os.path.realpath(__file__))
    path = "%s/ui/%s.py" % (basedir, filename)
    
    if os.path.exists(path): 
        return subprocess.Popen(["/usr/bin/python", path] + args).pid
    else:
        return False
