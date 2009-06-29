import os.path

def get_file_extension(path):
    """
    Wrapper that retrieves a file path's extension.  If the given path is not
    a file, don't try to find an extension, because it would be invalid.
    
    @type   path:   string
    @param  path:   A filename or path.
    
    @rtype:         string
    @return:        A file extension.
    
    """
    
    return (os.path.isfile(path) and os.path.splitext(path)[1] or "")

def get_common_directory(paths):
    common = os.path.commonprefix(abspaths(paths))
    
    while not os.path.exists(common) or os.path.isfile(common):
        common = os.path.split(common)[0]
        
        if common == "":
            break
        
    return common

def abspaths(paths):
    index = 0
    for path in paths:
        paths[index] = os.path.realpath(os.path.abspath(path))
        index += 1
    
    return paths

def get_home_folder():
    """ 
    Returns the location of the hidden folder we use in the home dir.
    This is used for storing things like previous commit messages and
    previously used repositories.
    
    @rtype:     string
    @return:    The location of our main user storage folder.
    
    """
    
    # Make sure we adher to the freedesktop.org XDG Base Directory 
    # Specifications. $XDG_CONFIG_HOME if set, by default ~/.config 
    xdg_config_home = os.environ.get(
        "XDG_CONFIG_HOME", 
        os.path.join(os.path.expanduser("~"), ".config")
    )
    config_home = os.path.join(xdg_config_home, "nautilussvn")
    
    # Make sure the directories are there
    if not os.path.isdir(config_home):
        # FIXME: what if somebody places a file in there?
        os.makedirs(config_home, 0700)

    return config_home
