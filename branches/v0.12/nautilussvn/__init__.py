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

import gettext
import locale

version = "0.12-dev"
APP_NAME = "NautilusSvn"
LOCALE_DIR = "locale"

gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)

def init_locale():
    lang, encoding = locale.getdefaultlocale()
    
    if encoding is None:
        encoding = "UTF-8"
    if encoding.lower() == "utf":
        encoding = "UTF-8"
    if encoding == "UTF8":
        encoding = "UTF-8"
    
    try:
        locale.setlocale(locale.LC_ALL, "%s.%s" % (lang, encoding))
    except locale.Error, e:
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except locale.Error, e:
            locale.setlocale(locale.LC_ALL, "C")
