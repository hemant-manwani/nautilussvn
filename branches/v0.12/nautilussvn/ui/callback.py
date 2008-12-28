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

from nautilussvn.ui import InterfaceView
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.lib.vcs
import nautilussvn.lib.helper

gtk.gdk.threads_init()

class Notification(InterfaceView):

    def __init__(self):
        InterfaceView.__init__(self, "notification", "Notification")
    
        self.table = nautilussvn.ui.widget.Table(
            self.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path", "Mime Type"]
        )
            
    def on_destroy(self, widget):
        self.close()
    
    def on_cancel_clicked(self, widget):
        self.close()
        
    def on_ok_clicked(self, widget):
        self.close()

    def toggle_ok_button(self, sensitive):
        gtk.gdk.threads_enter()
        self.get_widget("ok").set_sensitive(sensitive)
        gtk.gdk.threads_leave()
            
    def append(self, entry):
        gtk.gdk.threads_enter()
        self.table.append(entry)
        self.table.scroll_to_bottom()
        gtk.gdk.threads_leave()
    
    def set_title(self, title):
        gtk.gdk.threads_enter()
        self.get_widget("Notification").set_title(title)
        gtk.gdk.threads_leave()


class VCSAction(threading.Thread):
    """
    Provides a central interface to handle vcs actions & callbacks.
    Loads UI elements that require user interaction.
    
    """
    
    def __init__(self, client, register_gtk_quit=False):
        threading.Thread.__init__(self)
        
        self.message = "Empty Message"
        
        self.notification = Notification()
        
        # Tells the notification window to do a gtk.main_quit() when closing
        # Is used when the script is run from a command line
        if register_gtk_quit:
            self.notification.register_gtk_quit()
        
        self.client = client
        self.client.set_callback_notify(self.notify)
        self.client.set_callback_get_log_message(self.get_log_message)
        self.client.set_callback_get_login(self.get_login)
        self.client.set_callback_ssl_server_trust_prompt(self.get_ssl_trust)
        self.client.set_callback_ssl_client_cert_password_prompt(self.get_ssl_password)
        
        self.before = None
        self.after = None
        self.func = None
        self.pre_func = None
        self.post_func = None
    
    def cancel(self):
        return False
    
    def notify(self, data):
        self.notification.append([
            self.client.NOTIFY_ACTIONS[data["action"]],
            data["path"],
            data["mime_type"]
        ])
        
        if data["action"] in self.client.NOTIFY_ACTIONS_COMPLETE:
            self.finish("Revision %s" % data["revision"].number)
    
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
            
    def set_before_message(self, message):
        self.before = message
    
    def set_after_message(self, message):
        self.after = message
    
    def run_before(self, func, *args, **kargs):
        self.pre_func = func
        self.pre_args = args
        self.pre_kwargs = kwargs
    
    def run_after(self, func, *args, **kwargs):
        self.post_func = func
        self.post_args = args
        self.post_kwargs = kwargs
    
    def set_action(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
     
    def run(self):
        if self._func is None:
            return
    
        self.set_status(self.before)
        
        # If a "run_before" callback is set, call it
        if self.pre_func is not None:
            self.pre_func(*self.pre_args, **self.pre_kwargs)
        
        # Run the main callback function
        ret = self._func(*self._args, **self._kwargs)
        
        # If all went well, the callback function should return None
        if ret == None:
            self.finish(self.after)
            if self.message:
                nautilussvn.lib.helper.save_log_message(self.message)
        else:
            self.finish(ret)

        # If a "run_after" callback is set, call it
        if self.post_func is not None:
            self.post_func(*self.post_args, **self.post_kwargs)

