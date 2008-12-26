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

import threading

import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.lib.vcs
import nautilussvn.lib.helper

gtk.gdk.threads_init()

class Notification:

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "notification", "Notification")
    
        self.table = nautilussvn.ui.widget.Table(
            self.view.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path", "Mime Type"]
        )
            
    def on_destroy(self, widget):
        gtk.main_quit()
    
    def on_cancel_clicked(self, widget):
        gtk.main_quit()
        
    def on_ok_clicked(self, widget):
        gtk.main_quit()

    def toggle_ok_button(self, sensitive):
        gtk.gdk.threads_enter()
        self.view.get_widget("ok").set_sensitive(sensitive)
        gtk.gdk.threads_leave()
            
    def append(self, entry):
        gtk.gdk.threads_enter()
        self.table.append(entry)
        gtk.gdk.threads_leave()
    
    def set_title(self, title):
        gtk.gdk.threads_enter()
        self.view.get_widget("Notification").set_title(title)
        gtk.gdk.threads_leave()
    
    def show(self):
        self.view.show()


class VCSAction(threading.Thread):
    """
    Provides a central interface to handle vcs actions & callbacks.
    Loads UI elements that require user interaction.
    
    """
    
    def __init__(self, client):
        threading.Thread.__init__(self)
        
        self.message = "Empty Message"
        
        self.started = False
        
        self.client = client
        
        self.notification = Notification()
        
        self.client.set_callback_notify(self.notify)
        self.client.set_callback_get_log_message(self.get_log_message)
        self.client.set_callback_get_login(self.get_login)
        self.client.set_callback_ssl_server_trust_prompt(self.get_ssl_trust)
        self.client.set_callback_ssl_client_cert_password_prompt(self.get_ssl_password)
    
    def cancel(self):
        return False
    
    def notify(self, data):
        self.notification.append([
            self.client.NOTIFY_ACTIONS[data["action"]],
            data["path"],
            data["mime_type"]
        ])
        
        if data["action"] in self.client.NOTIFY_ACTIONS_COMPLETE:
            self.finish()
    
    def finish(self, message=None):
        self.set_status(message)
        self.notification.toggle_ok_button(True)
    
    def get_log_message(self):
        return True, self.message
    
    def get_login(self, realm, username, may_save):
        dialog = nautilussvn.ui.dialog.Authentication(
            realm,
            may_save
        )
        
        return dialog.run()
    
    def get_ssl_trust(self, data):
    
        ACCEPTED_FAILURES = 3
    
        dialog = nautilissvn.ui.dialog.Certificate(
            data["realm"],
            data["hostname"],
            data["issuer_dname"],
            data["valid_from"],
            data["valid_to"],
            data["finger_print"]
        )
        
        result = dialog.run()
        if result == 0:
            #Deny
            return (False, ACCEPTED_FAILURES, False)
        elif result == 1:
            #Accept Once
            return (True, ACCEPTED_FAILURES, False)
        elif result == 2:
            #Accept Forever
            return (True, ACCEPTED_FAILURES, True)

    def get_ssl_password(self, realm, may_save):
        dialog = nautilussvn.ui.dialog.CertAuthentication(
            realm,
            may_save
        )
        
        return dialog.run()
        
    def set_log_message(self, message):
        self.message = message
    
    def set_status(self, message):
        if message is not None:
            self.notification.append([
                "", message, ""
            ])
            
    def set_before(self, message):
        self.before = message
    
    def set_after(self, message):
        self.after = message
            
    def set_action(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
     
    def run(self):
        if self._func is None:
            return
    
        self.set_status(self.before)
        ret = self._func(*self._args, **self._kwargs)
        
        if ret == None:
            self.finish(self.after)
            if self.message:
                nautilussvn.lib.helper.save_log_message(self.message)
        else:
            self.finish(ret)
