#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
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

"""

See: 

  * https://linkchecker.svn.sourceforge.net/svnroot/linkchecker/trunk/linkchecker/linkcheck/decorators.py
  * http://wiki.python.org/moin/PythonDecoratorLibrary
  
"""

import warnings

def update_func_meta (fake_func, real_func):
    """
    Set meta information (eg. __doc__) of fake function to that
    of the real function.
    @return fake_func
    """
    fake_func.__module__ = real_func.__module__
    fake_func.__name__ = real_func.__name__
    fake_func.__doc__ = real_func.__doc__
    fake_func.__dict__.update(real_func.__dict__)
    return fake_func

def deprecated (func):
    """
    A decorator which can be used to mark functions as deprecated.
    It emits a warning when the function is called.
    """
    def newfunc (*args, **kwargs):
        """
        Print deprecated warning and execute original function.
        """
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    return update_func_meta(newfunc, func)
