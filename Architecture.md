# Overall architecture #

![http://nautilussvn.googlecode.com/svn/wiki/images/architecture/overall_architecture.png](http://nautilussvn.googlecode.com/svn/wiki/images/architecture/overall_architecture.png)

# Components #

## Extension ##

### Context menu ###

A context menu is generated for one or more paths and will be build as following:

`[...]`

See the page ContextMenuStructure for a description of the conditions.

## GUI ##

`[...]`

## D-Bus Service ##

### Status checker ###

> _Responsibilities: do status checks, maintain status tree_

A status check can go three ways:

  1. If we've already looked the path up, return the statuses associated with it.
  1. If we haven't already got the path, return `[(path, "calculating")]`.
  1. If the item a status check is being requested for is not a or in a working copy then the result `[(path, "unknown")]` will be returned.

A recursive status check should always be done first to build up a valid status\_tree, otherwise recursive and non-recursive checks would conflict.

### Status Monitor ###

> _Responsibilities: manage watches, process events, request status checks, notify clients_

The only way to have the status for items stay up-to-date is by actively monitoring all items within a working copy and the related metadata (contained in the working copy administration areas, the .svn directories). The mechanism we use for this is gio.GFileMonitor.

Upon encountering a working copy for the first time a recursive status check is done in the background to build the status tree for that working copy. After that the status monitor will watch for any changes to all files/directories and the .svn/entries file (which is the only file modified when doing SVN operations) and modify the status tree accordingly.

When the monitor detects a change has  occurred, either to a versioned item itself or the associated metadata, it will process the event. If the item in question is not versioned it will skip it (this handles temporary files etc. quite nicely), if the item is however versioned it will add an invalidating status request to the queue for this file and non-invalidating ones for all parent directories.

When the request is processed it will notify all subscribers about the results.

## VCS Abstraction Layer ##

> _See [anyvc](http://bitbucket.org/RonnyPfannschmidt/anyvc/)_

# Unsorted #

  * Skipping intensive operations while on battery power may be a good idea.

  * I wonder if it's possible to analyze the .svn/entries file to determine precisely what files were modified.