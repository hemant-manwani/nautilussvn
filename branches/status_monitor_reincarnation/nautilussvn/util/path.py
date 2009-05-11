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
