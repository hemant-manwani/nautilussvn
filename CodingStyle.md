# Introduction #

If anything in this document differs from [PEP 8](http://www.python.org/dev/peps/pep-0008/) (Style Guide for Python Code) then please correct it as the PEP is leading.

# General #

> _(?) means that we haven't decided on this yet_

## From PEP-8 ##

  * Use 4 spaces per indentation level.
  * Never mix tabs and spaces. Spaces only.
  * Limit all lines to a maximum of 79 characters.
  * Imports are always put at the top of the file, just after any module comments and docstrings
  * Imports should usually be on separate lines
  * Imports should be grouped in the following order (you should put a blank line between each group of imports):
    * 1. standard library imports
    * 2. related third party imports
    * 3. local application/library specific imports

## Debugging ##

  * Don't use print statements, use the logging facility. At the top of a module, use:

```
from nautilussvn.lib.log import Log
log = Log("nautilussvn.mymodule") # Replace "mymodule", obviously
```

```
log.debug("Number of items: %i" % len(items))
```

...or even:

```
    try:
        risky_thing()
    except Exception, e:
        log.exception(e)
```

  * Sometimes, if you put in some code for debugging, you could even leave it in as a comment for future maintainers, eg. from the status checker code:

```
    # Uncomment this for useful simulation of a looooong status check :) 
    # log.debug("Sleeping for 10s...")
    # time.sleep(5)
    # log.debug("Done.")
```

  * If you use Eclipse + pydev, use task tags to remind yourself to remove or flesh things out (eg. `#FIXME: simplify code after debugging`)

# Specific #

  * Double quotes should be used to indicate strings, i.e. "This is a string."
  * When referring to both files and directories use the term "items" not "files". Also sometimes you want to use "paths".
  * (?) To stay consistent with imports always use absolute imports.

# Comments #

  * http://epydoc.sourceforge.net/
  * http://docs.python.org/library/doctest.html

# Style Guide #

## Example ##
> _See [this code review](http://code.google.com/p/nautilussvn/source/browse/branches/v0.12/nautilussvn/lib/extensions/nautilus/__init__.py?spec=svn315&r=315) for an in-depth explanation of what qualifies as good code_

```
#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2008 by Adam Plumb <adamplumb@gmail.com>
# 
# NautilusSvn is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# NautilusSvn is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NautilusSvn;  If not, see <http://www.gnu.org/licenses/>.
#

```