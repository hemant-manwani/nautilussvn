# Introduction #

Obviously all bugs in our [issue tracker](http://code.google.com/p/nautilussvn/issues/list?can=2&q=-status%3ANew+-status%3ANeedInfo+type%3ADefect) are known issues, however here are some of the really important ones.

# Known issues #



## The main context menu will appear with items in incorrect places ##

> See: [Issue #96](http://code.google.com/p/nautilussvn/issues/detail?id=96)

This is a bug in Nautilus (we think) and so far we haven’t found a workaround. If you get this, most of the time you can click away (in the Nautilus background) and then click back on the original item, and this will give you a correct menu.

If you want to try to find a workaround for us, we’ve created a simple test extension at http://nautilussvn.googlecode.com/files/contextmenubugtest.py. Put this in your ~/.nautilus/python-extensions folder and type ‘nautilus -q && nautilus --no-desktop’ to load it up.  If you can find a workaround, you will be a hero!

## Dialogs display full paths, not relative ##

The dialogs should ideally only display the paths relative to the in Nautilus currently visible directory. This behavior was implemented before, however the way it was (using os.chdir calls) was causing Nautilus to reject to unmount removable devices ([Issue #89](http://code.google.com/p/nautilussvn/issues/detail?id=89)) so we removed it and are working on a replacement.

## No submenu for NautilusSvn menu item on background or File menu ##

This problem only occurs on older versions of Nautilus e.g. 2.22.2 (or everything <= 2.24.1). Nautilus 2.22.2 is the version included with Ubuntu 8.04.

## Limitations of the current status checker ##

There are three situations where we currently can’t keep emblems up-to-date:

### When any file that isn't visible is modified ###

  * An example: if you’re in /foo and the file /foo/bar/baz is modified (e.g. edited and saved) the status for /foo and /foo/bar will be incorrect. Nautilus doesn’t inform us about these modifications (which makes sense for normal extensions). We have been working on a new status monitor so in the future we will be able to do this.

### Adding items ###

  * Another example: if you’re in /foo and /foo/bar is “normal” and you add /foo/bar/baz by selecting NautilusSvn -> Add from the context menu of /foo the statuses for /foo and /foo/bar willbe incorrect. We’re only rechecking the paths you originally selected and any item you saw that was either “added”,  “deleted”, “replaced”, “modified”, “missing”, “unversioned”, or “incomplete”. There might be something I can think up here that might not impact performance all too badly.

### Using the command-line svn client ###

  * We've currently implemented something similar to a callback system for any functions called from the context menu. Once a function is done, we'll recheck the status for the relevant items. This obviously doesn't work when one uses the command-line client. With the exception of svn revert we currently cannot keep emblems up-to-date when you use the command-line client, you'll have to use F5 to refresh. Again, the new status monitor will eliminate this problem.