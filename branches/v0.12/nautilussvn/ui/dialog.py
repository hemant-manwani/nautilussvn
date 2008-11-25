#!/usr/bin/env python

import pygtk
import gobject
import gtk

import widget
import helper
import view

class PreviousMessages:
    def __init__(self):
        self.view = view.InterfaceView(self, "PreviousMessages")
        
    def run(self):
        self.message = widget.TextView(self.view.get_widget("prevmes_message"))

        self.message_table = widget.Table(
            self.view.get_widget("prevmes_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Date", "Message"]
        )
        
        self.entries = helper.GetPreviousMessages()
        for entry in self.entries:
            self.message_table.append(entry)
        
        returner = None
        self.dialog = self.view.get_widget("PreviousMessages")
        result = self.dialog.run()
        if result == 1:
            returner = self.message.get_text()
        self.dialog.destroy()

        return returner

    def on_prevmes_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            
            self.message.set_text(treeview.get_model()[path][1])
        
class FileChooser:
    def __init__(self):
        self.dialog = gtk.FileChooserDialog("Select a Folder", 
            None, 
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        self.dialog.set_default_response(gtk.RESPONSE_OK)

    def run(self):
        returner = None
        result = self.dialog.run()
        if result == gtk.RESPONSE_OK:
            returner = self.dialog.get_uri()
        self.dialog.destroy()
        return returner
        
class Certificate:
    def __init__(self, realm="", host="", 
            issuer_from="", issuer_to="", valid="", fingerprint=""):
            
        self.view = view.InterfaceView(self, "Certificate")
        
        self.view.get_widget("cert_realm").set_label(realm)
        self.view.get_widget("cert_host").set_label(host)
        self.view.get_widget("cert_issuer").set_label("%s to %s" % (issuer_from,issuer_to))
        self.view.get_widget("cert_valid").set_label(valid)
        self.view.get_widget("cert_fingerprint").set_label(fingerprint)
        
    def run(self):
        self.dialog = self.view.get_widget("Certificate")
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
        self.view = view.InterfaceView(self, "Authorization")
        
        self.view.get_widget("auth_location").set_label(location)
        self.view.get_widget("auth_realm").set_label(realm)
        
    def run(self):
        self.dialog = self.view.get_widget("Authorization")
        result = self.dialog.run()
        
        if result == 1:
            self.send_details()
            
        self.dialog.destroy()
        return
        
    def send_details(self):
        self.login = self.view.get_widget("auth_login").get_text()
        self.password = self.view.get_widget("auth_password").get_text()

        print "Sending %s:%s" % (self.login, self.password)
        
        
class Property:

    PROPS = ['', 'svn:executable','svn:mime',
        'svn:ignore','svn:keywords','svn:eol',
        'svn:externals','svn:special']

    def __init__(self, name="", value=""):
        self.view = view.InterfaceView(self, "Property")
        
        self.save_name = name
        self.save_value = value
        
        self.names = widget.ComboBox(self.view.get_widget("property_names"), self.PROPS)
        self.names.set_active_from_value(name)
        self.value = widget.TextView(self.view.get_widget("property_value"), value)
        
    def run(self):
        self.dialog = self.view.get_widget("Property")
        result = self.dialog.run()
        
        if result == 1:
            self.save()
        
        self.dialog.destroy()
        return (self.save_name, self.save_value)
    
    def save(self):
        self.save_name = self.names.get_active_text()
        self.save_value = self.value.get_text()
        
