from os.path import isdir, isfile, realpath, basename

#: A list of statuses which count as modified (for a directory) in 
#: TortoiseSVN emblem speak.
MODIFIED_STATUSES = [
    "added",
    "deleted",
    "replaced",
    "modified",
    "missing"
]

def get_summarized_status(path, statuses):
    """
    This is a helper function to figure out the textual representation 
    for a set of statuses. In TortoiseSVN speak a directory is
    regarded as modified when any of its children are either added, 
    deleted, replaced, modified or missing so you can quickly see if 
    your working copy has local changes.
    
    @type   path:       string
    @param  path:       The path for which to summarize
    
    @type   statuses:   list
    @param  statuses:   A list of (abspath, state) tuples
    """
    
    # Unlike Subversion most VCS's don't have the concept of statuses
    # on directories, so make sure to take this into account.
    # FIXME: but why are we doing this:
    statuses = [(status[0], status[1]) for status in statuses if status[0].startswith(path)]
    text_statuses = [status[1] for status in statuses]
    statuses_dictionary = dict(statuses)
    
    # If no statuses are returned but we do have a workdir_manager
    # it means that an error occured, most likely a working copy
    # administration area (.svn directory) went missing but it could
    # be pretty much anything.
    if not statuses: 
        # FIXME: figure out a way to make only the directory that
        # is missing display conflicted and the rest unkown.
        return "unknown"

    # We need to take special care of directories
    if isdir(path):
        # These statuses take precedence.
        if "conflicted" in text_statuses: return "conflicted"
        if "obstructed" in text_statuses: return "obstructed"
        
        # The following statuses take precedence over the status
        # of children.
        if (path in statuses_dictionary and 
                statuses_dictionary[path] in ["added", "modified", "deleted"]):
            return statuses_dictionary[path]
        
        # A directory should have a modified status when any of its children
        # have a certain status (see modified_statuses above). Jason thought up 
        # of a nifty way to do this by using sets and the bitwise AND operator (&).
        if len(set(MODIFIED_STATUSES) & set(text_statuses)):
            return "modified"
    
    # If we're not a directory we end up here.
    if path in statuses_dictionary: return statuses_dictionary[path]
    return "normal"
