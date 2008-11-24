#!/usr/bin/env python

import sys
import pygtk
import gtk
import gobject
import gtk.glade
import widgets
import helper

class PreviousMessages:
    def __init__(self):
        self.wTree = gtk.glade.XML("glade/interface.glade", "PreviousMessages")
        self.wTree.signal_autoconnect(self)
        
    def run(self):
        self.message = self.wTree.get_widget("prevmes_message")
        self.buffer = gtk.TextBuffer()
        self.message.set_buffer(self.buffer)

        self.message_table = widgets.Table(
            self.wTree.get_widget("prevmes_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Date", "Message"]
        )
        
        self.entries = helper.GetPreviousMessages()
        for entry in self.entries:
            self.message_table.append(entry)
        
        returner = None
        self.dialog = self.wTree.get_widget("PreviousMessages")
        result = self.dialog.run()
        if result == 1:
            returner = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter())
        self.dialog.destroy()

        return returner

    def on_prevmes_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            
            self.buffer.set_text(treeview.get_model()[path][1])
            

class Progress:
    
    OK_BUTTON_ENABLED = False

    def __init__(self):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Progress")
        self.wTree.signal_autoconnect(self)
        
    def run(self):
        self.ok_button = self.wTree.get_widget("progress_ok")
    
        self.messages_table = widgets.Table(
            self.wTree.get_widget("progress_messages_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path"]
        )
        
        self.entries = [
            ['Added', '/home/adam/Development/test.html'],
            ['Commited', '/home/adam/Development/blah.txt']
        ]
        for row in self.entries:
            self.append_to_table(row)
        
        self.dialog = self.wTree.get_widget("Progress")
        result = self.dialog.run()
        self.dialog.destroy()
        
        return result
        
    def toggle_ok_button(self):
        self.OK_BUTTON_ENABLED = not self.OK_BUTTON_ENABLED
        self.ok_button.set_sensitive(self.OK_BUTTON_ENABLED)
            
    def append_to_table(self, entry):
        self.messages_table.append(entry)
        
class FileChooser:
    def __init__(self):
        self.dialog = gtk.FileChooserDialog("Select a Folder", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        self.dialog.set_default_response(gtk.RESPONSE_OK)

    def run(self):
        returner = None
        result = self.dialog.run()
        if result == gtk.RESPONSE_OK:
            returner = self.dialog.get_uri()
        self.dialog.destroy()
        return returner
        
class Certificate:
    def __init__(self, realm="", host="", issuer="", valid="", fingerprint=""):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Certificate")
        self.wTree.signal_autoconnect(self)
        
        self.wTree.get_widget("cert_realm").set_label(realm)
        self.wTree.get_widget("cert_host").set_label(host)
        self.wTree.get_widget("cert_issuer").set_label(issuer)
        self.wTree.get_widget("cert_valid").set_label(valid)
        self.wTree.get_widget("cert_fingerprint").set_label(fingerprint)
        
    def run(self):
        self.dialog = self.wTree.get_widget("Certificate")
        result = self.dialog.run()
        
        if result == -1:
            self.deny()
        elif result == 1:
            self.accept_once()
        elif result == 2:
            self.accept_forever()
        
        self.dialog.destroy()
        return

    def deny(self):
        print "Deny"
   
    def accept_once(self):
        print "Accept Once"
    
    def accept_forever(self):
        print "Accept Forever"
        
class Authorization:
    def __init__(self, location="", realm=""):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Authorization")
        self.wTree.signal_autoconnect(self)
        
        self.wTree.get_widget("auth_location").set_label(location)
        self.wTree.get_widget("auth_realm").set_label(realm)
        
    def run(self):
        self.dialog = self.wTree.get_widget("Authorization")
        result = self.dialog.run()
        
        if result == 1:
            self.send_details()
            
        self.dialog.destroy()
        return
        
    def send_details(self):
        self.login = self.wTree.get_widget("auth_login").get_text()
        self.password = self.wTree.get_widget("auth_password").get_text()

        print "Sending %s:%s" % (self.login, self.password)
        
        
class Property:

    PROPS = ['', 'svn:executable','svn:mime','svn:ignore','svn:keywords','svn:eol','svn:externals','svn:special']

    def __init__(self, name="", value=""):
        self.wTree = gtk.glade.XML("glade/interface.glade", "Property")
        self.wTree.signal_autoconnect(self)
        
        self.save_name = name
        self.save_value = value
        
        self.names = widgets.ComboBox(self.wTree.get_widget("property_names"), self.PROPS)
        self.names.set_active_from_value(name)
        self.value = widgets.TextView(self.wTree.get_widget("property_value"), value)
        
    def run(self):
        self.dialog = self.wTree.get_widget("Property")
        result = self.dialog.run()
        
        if result == 1:
            self.save()
        
        self.dialog.destroy()
        return (self.save_name, self.save_value)
    
    def save(self):
        self.save_name = self.names.get_active_text()
        self.save_value = self.value.get_text()
        
