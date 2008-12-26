#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdk@gmail.com>
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

import pygtk
import gobject
import gtk

import nautilussvn.ui.dialog

class CertificateTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Certificate(
            realm="this realm", host="this host", 
            issuer_from="2008-10-20", issuer_to="2008-12-12", 
            valid="valid from xxx to xxx", fingerprint="this fingerprint"
        )
            
        result = self.dialog.run()

class AuthorizationTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Authorization(
            location="this location", 
            realm="this realm"
        )
            
        result = self.dialog.run()

class PropertyTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Property(name="prop name", value="")
        result = self.dialog.run()

class PreviousMessagesTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.PreviousMessages()
        result = self.dialog.run()
        
class ConfirmationTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Confirmation()
        result = self.dialog.run()
        
class MessageBoxTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.MessageBox("This is a test message")
        
if __name__ == "__main__":
    window = AuthorizationTest()
    gtk.main()
