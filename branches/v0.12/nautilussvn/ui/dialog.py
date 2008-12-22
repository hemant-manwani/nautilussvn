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

import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.log
import nautilussvn.lib.helper

GLADE = 'dialogs'

class PreviousMessages:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "PreviousMessages")
        
    def run(self):
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("prevmes_message")
        )

        self.message_table = nautilussvn.ui.widget.Table(
            self.view.get_widget("prevmes_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Date", "Message"]
        )
        self.entries = nautilussvn.lib.helper.get_previous_messages()
        for entry in self.entries:
            tmp = entry[1]
            if len(tmp) > 80:
                tmp = "%s..." % tmp[0:80]
        
            self.message_table.append([entry[0],tmp])
        
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
            self.message.set_text(self.entries[path[0]][1])
        
class FolderChooser:
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
    """
    Provides a dialog to accept/accept_once/deny an ssl certificate
    
    """
    
    def __init__(self, realm="", host="", 
            issuer="", valid_from="", valid_to="", fingerprint=""):
            
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "Certificate")
        
        self.view.get_widget("cert_realm").set_label(realm)
        self.view.get_widget("cert_host").set_label(host)
        self.view.get_widget("cert_issuer").set_label(issuer)
        self.view.get_widget("cert_valid").set_label(
            "%s to %s" % (valid_from, valid_to)
        )
        self.view.get_widget("cert_fingerprint").set_label(fingerprint)
        
    def run(self):
        """
        Returns three possible values:
            0   Deny
            1   Accept Once
            2   Accept Forever
            
        """
        
        self.dialog = self.view.get_widget("Certificate")
        result = self.dialog.run()
        self.dialog.destroy()
        return result
        
class Authorization:
    def __init__(self, realm="", may_save=True):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "Authorization")
        
        self.view.get_widget("auth_realm").set_label(realm)
        self.view.get_widget("auth_save").set_sensitive(may_save)
        
    def run(self):
        returner = None
        
        self.dialog = self.view.get_widget("Authorization")
        result = self.dialog.run()
        
        if result == 1:
            returner = (
                True,
                self.view.get_widget("auth_login").get_text(),
                self.view.get_widget("auth_password").get_text(),
                self.view.get_widget("auth_save").get_active()
            )
        else:
            returner = (
                False,
                "",
                "",
                False
            )
            
        self.dialog.destroy()
        return returner
                
class CertAuthorization:
    def __init__(self, realm="", may_save=True):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "CertAuthorization")
        
        self.view.get_widget("certauth_realm").set_label(realm)
        self.view.get_widget("certauth_save").set_sensitive(may_save)
        
    def run(self):
        returner = None
        
        self.dialog = self.view.get_widget("CertAuthorization")
        result = self.dialog.run()
        
        if result == 1:
            returner = (
                True,
                self.view.get_widget("certauth_password").get_text(),
                self.view.get_widget("certauth_save").get_active()
            )
        else:
            returner = (
                False,
                "",
                False
            )
            
        self.dialog.destroy()
        return returner
        
class Property:
    def __init__(self, name="", value=""):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "Property")
        
        self.save_name = name
        self.save_value = value
        
        self.name = self.view.get_widget("property_name")
        self.name.set_text(name)
        
        self.value = nautilussvn.ui.widget.TextView(
            self.view.get_widget("property_value"), 
            value
        )
        
    def run(self):
        self.dialog = self.view.get_widget("Property")
        result = self.dialog.run()
        
        if result == 1:
            self.save()
        
        self.dialog.destroy()
        return (self.save_name, self.save_value)
    
    def save(self):
        self.save_name = self.name.get_text()
        self.save_value = self.value.get_text()

class FileChooser:
    def __init__(self, title="Select a File", folder=None):
        self.dialog = gtk.FileChooserDialog(title, 
            None, 
            gtk.FILE_CHOOSER_ACTION_OPEN, 
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        if folder is not None:
            self.dialog.set_current_folder(folder)
        self.dialog.set_default_response(gtk.RESPONSE_OK)

    def run(self):
        returner = None
        result = self.dialog.run()
        if result == gtk.RESPONSE_OK:
            returner = self.dialog.get_uri()
        self.dialog.destroy()
        return returner
        
class Confirmation:
    def __init__(self, message="Are you sure you want to continue?"):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "Confirmation")
        self.view.get_widget("confirm_message").set_text(message)
        
    def run(self):
        dialog = self.view.get_widget("Confirmation")
        result = dialog.run()
        
        dialog.destroy()
        
        return result
        
class MessageBox:
    def __init__(self, message):
        self.view = nautilussvn.ui.InterfaceView(self, GLADE, "MessageBox")
        self.view.get_widget("messagebox_message").set_text(message)

        dialog = self.view.get_widget("MessageBox")
        dialog.run()
        dialog.destroy()
        
class LogDialog(nautilussvn.ui.log.Log):
    def __init__(self, ok_callback=None, multiple=False):
        """
        Override the normal Log class so that we can hide the window as we need.
        Also, provide a callback for when the OK button is clicked so that we
        can get some desired data.
        """
        nautilussvn.ui.log.Log.__init__(self)
        self.ok_callback = ok_callback
        self.multiple = multiple
        
    def on_destroy(self, widget):
        pass
    
    def on_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        if self.ok_callback is not None:
            if self.multiple == True:
                self.ok_callback(self.get_selected_revision_numbers())
            else:
                self.ok_callback(self.get_selected_revision_number())
