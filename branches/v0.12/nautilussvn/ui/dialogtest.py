#!/usr/bin/env python

import sys

import pygtk
import gobject
import gtk
import gtk.glade

import dialogs

class ProgressTest:
    def __init__(self):
        dialog = dialogs.Progress()
        result = dialog.run()
        return
        
class CertificateTest:
    def __init__(self):
        dialog = dialogs.Certificate(realm="this realm", host="this host", issuer="this issuer", valid="valid from xxx to xxx", fingerprint="this fingerprint")
        result = dialog.run()
        return

if __name__ == "__main__":
    window = CertificateTest()
    gtk.main()
