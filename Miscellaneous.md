# NautilusSvn v0.12 branch #

[Installation instructions for v0.12 have moved](v012_Installation.md)

# No never ending loop? #
In a [particular revision](http://code.google.com/p/nautilussvn/source/browse/branches/v0.12/nautilussvn/lib/extensions/nautilus/NautilusSvn.py?spec=svn362&r=362#218) there was a function update\_emblem which was called by update\_file\_info but which indirectly called update\_file\_info back by calling NautilusVFSFile.invalidate\_extension\_info. Everything logical told me this should cause a neverending loop, but that wasn't the case. I never found out why that did not happen.

# Singleton in Python #
I was going to do this:

```
def __init__(self):
    """
    This class is a singleton, there can be only one instance. The reason
    for this is because we need to maintain a cache of statuses and
    multiple instances would mess around with this.
    
    See (yes, that's from 1997):
    
    http://www.python.org/workshops/1997-10/proceedings/savikko.html
    
    FIXME: I know there's more Pythonic and better ways to do this (shared
    state, not single instances for example) But I just don't understand
    how to implement those correctly yet. So when I do, I'll do them ;-)
    """
    if SVN.__single:
        print "already created"
        # TODO: uh the example didn't do this, is this really a good idea?
        self = SVN.__single
        
    SVN.__single = self
    self.client = pysvn.Client()
```

But this didn't work and I gave up because it wasn't important yet (and as the docstring indicates I'm aware of the fact that this can be done in a better way). Putting this code here because I never committed it and still wanted to have it around.

This was the exception that might me give up by the way:

```
Traceback (most recent call last):
  File "/home/bruce/.nautilus/python-extensions/NautilusSvn.py", line 209, in get_file_items
    return MainContextMenu(paths, self).construct_menu()
  File "/home/bruce/.nautilus/python-extensions/NautilusSvn.py", line 683, in construct_menu
    return self.create_menu_from_definition(menu_definition)
  File "/home/bruce/.nautilus/python-extensions/NautilusSvn.py", line 713, in create_menu_from_definition
    if definition_item["condition"]():
  File "/home/bruce/.nautilus/python-extensions/NautilusSvn.py", line 749, in condition_checkout
    not self.vcs_client.is_working_copy(self.paths[0])):
  File "/home/bruce/Development/nautilussvn/branches/v0.12/nautilussvn/lib/vcs/svn.py", line 178, in is_working_copy
    entry = self.client.info(path)
AttributeError: SVN instance has no attribute 'client'
```

# Modules as "singleton" #
Since modules are only loaded once (per interpreter?) any variables defined in them are only set once.

# Threading and PySVN #

```
pysvn.ClientError: client in use on another thread
```

# Killing the running DBus service #
You can do this using:
```
pgrep -f service.py | xargs kill; 
```

Or when testing:
```
pgrep -f service.py | xargs kill; nautilus --no-desktop .; pgrep -f service.py | xargs kill
```