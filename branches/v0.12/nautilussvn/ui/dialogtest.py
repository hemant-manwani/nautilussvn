#!/usr/bin/env python

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
        return

class AuthorizationTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Authorization(
            location="this location", 
            realm="this realm"
        )
            
        result = self.dialog.run()
        return

class PropertyTest:
    def __init__(self):
        self.dialog = nautilussvn.ui.dialog.Property(name="prop name", value="")
        result = self.dialog.run()
        return
        
if __name__ == "__main__":
    window = CertificateTest()
    gtk.main()
