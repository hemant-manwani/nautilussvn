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

    def __init__(self, callback_cancel=None):
        InterfaceView.__init__(self, "notification", "Notification")
    
        self.table = nautilussvn.ui.widget.Table(
            self.get_widget("table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path", "Mime Type"]
        )
        
        self.callback_cancel = callback_cancel
            
    def on_destroy(self, widget):
        self.close()
    
    def on_cancel_clicked(self, widget):
        if self.callback_cancel is not None:
            self.callback_cancel()
        
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
        
        self.client = client
        self.client.set_callback_cancel(self.cancel)
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
        
        self.login_tries = 0
        self.cancel = False

        self.notification = Notification(callback_cancel=self.set_cancel)
        
        # Tells the notification window to do a gtk.main_quit() when closing
        # Is used when the script is run from a command line
        if register_gtk_quit:
            self.notification.register_gtk_quit()
    
    def cancel(self):
        """
        PySVN calls this callback method frequently to see if the user wants
        to cancel the action.  If self.cancel is True, then it will cancel
        the action.  If self.cancel is False, it will continue.
        
        """
        
        return self.cancel

    def set_cancel(self, cancel=True):
        """
        Used as a callback function by the Notification UI.  When the cancel
        button is clicked, it sets self.cancel to True, and the cancel callback
        method returns True.
        
        """
        
        self.cancel = cancel
    
    def notify(self, data):
        """
        This method is called every time the VCS function wants to tell us
        something.  It passes us a dictionary of useful information.  When
        this method is called, it appends some useful data to the notifcation
        window.
        
        TODO: We need to implement this in a more VCS-agnostic way, since the
        supplied data dictionary is pysvn-dependent.  I'm going to implement
        something in lib/vcs/svn.py soon.
        
        """
        
        self.notification.append([
            self.client.NOTIFY_ACTIONS[data["action"]],
            data["path"],
            data["mime_type"]
        ])
        
        if data["action"] in self.client.NOTIFY_ACTIONS_COMPLETE:
            self.finish("Revision %s" % data["revision"].number)
    
    def finish(self, message=None):
        """
        This is called when the final notifcation message has been received,
        or it is called manually when no final notification message is expected.
        
        It sets the current "status", and enables the OK button to allow
        the user to leave the window.
        
        @type   message: string
        @param  message: A message to show the user.
        
        """
        
        self.set_status(message)
        self.notification.toggle_ok_button(True)
    
    def get_log_message(self):
        """
        A callback method that retrieves a supplied log message.
        
        Returns a list where the first element is True/False.  Returning true
        tells the action to continue, false tells it to cancel.  The second
        element is the log message, which is specified by self.message.
        self.message is set by calling the self.set_log_message() method from
        the UI interface class.
        
        @rtype:  (boolean, string)
        @return: (True=continue/False=cancel, log message)
        
        """
        
        return True, self.message
    
    def get_login(self, realm, username, may_save):
        """
        A callback method that requests a username/password to login to a 
        password-protected repository.  This method runs the Authentication
        dialog, which provides a username, password, and saving widget.  The
        dialog returns a tuple, which is returned directly to the VCS caller.
        
        If the login fails greater than three times, cancel the action.
        
        The dialog must be called from within a threaded block, otherwise it
        will not be responsive.
        
        @type   realm:      string
        @param  realm:      The realm of the repository.
        
        @type   username:   string
        @param  username:   Username passed by the vcs caller.
        
        @type   may_save:   boolean
        @param  may_save:   Whether or not the authentication can be saved.
        
        @rtype:             (boolean, string, string, boolean)
        @return:            (True=continue/False=cancel, username,password, may_save)
        
        """
    
        if self.login_tries >= 3:
            return (False, "", "", False)
    
        gtk.gdk.threads_enter()
        dialog = nautilussvn.ui.dialog.Authentication(
            realm,
            may_save
        )
        result = dialog.run()
        gtk.gdk.threads_leave()
        
        if result is not None:
            self.login_tries += 1
        
        return result
    
    def get_ssl_trust(self, data):
        """
        A callback method that requires the user to either accept or deny
        a certificate from an ssl secured repository.  It opens a dialog that
        shows the user information about the ssl certificate and then gives
        them the option of denying, accepting, or accepting once.

        The dialog must be called from within a threaded block, otherwise it
        will not be responsive.

        @type   data:   dictionary
        @param  data:   A dictionary with SSL certificate info.
        
        @rtype:         (boolean, int, boolean)
        @return:        (True=Accept/False=Deny, number of accepted failures, remember)
        
        """
    
        ACCEPTED_FAILURES = 3
    
        gtk.gdk.threads_enter()
        dialog = nautilissvn.ui.dialog.Certificate(
            data["realm"],
            data["hostname"],
            data["issuer_dname"],
            data["valid_from"],
            data["valid_to"],
            data["finger_print"]
        )
        result = dialog.run()
        gtk.gdk.threads_leave()

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
        """
        A callback method that is used to get an ssl certificate passphrase.
        
        The dialog must be called from within a threaded block, otherwise it
        will not be responsive.       

        @type   realm:      string
        @param  realm:      The certificate realm.
        
        @type   may_save:   boolean
        @param  may_save:   Whether or not the passphrase can be saved.
        
        @rtype:             (boolean, string, boolean)
        @return:            (True=continue/False=cancel, password, may save)
        
        """
        
        gtk.gdk.threads_enter()
        dialog = nautilussvn.ui.dialog.CertAuthentication(
            realm,
            may_save
        )
        result = dialog.run()
        gtk.gdk.threads_leave()

        return result
        
    def set_log_message(self, message):
        """
        Set this action's log message from the UI interface.  self.message
        is referred to when the VCS does the get_log_message callback.
        
        @type   message: string
        @param  message: Set a log message.
        
        """
        
        self.message = message
    
    def set_status(self, message):
        """
        Set the current status of the VCS action.  Currently, this method
        is called at the beginning and end of each action, to display what is
        going on.  Currently, it just appends the status message to the 
        notification window.  In the future, I may set up a progress bar
        and put the status message there.
        
        @type   message: string
        @param  message: A status message.
        
        """
        
        if message is not None:
            self.notification.append([
                "", message, ""
            ])
            
    def set_before_message(self, message):
        """
        Set a message to be displayed before the VCS action starts running.
        This is generally called from the ui class.

        @type   message: string
        @param  message: A status message.
        
        """
        
        self.before = message
    
    def set_after_message(self, message):
        """
        Set a message to be displayed before the VCS action after running.
        This is generally called from the ui class.

        @type   message: string
        @param  message: A status message.
        
        """

        self.after = message
    
    def run_before(self, func, *args, **kargs):
        """
        Set a callback function to be run before the VCS action begins running.
        The actual function is called from the self.run() method.
        
        @type   func: function
        @param  func: The function to run before the VCS action begins running.
        
        """

        self.pre_func = func
        self.pre_args = args
        self.pre_kwargs = kwargs
    
    def run_after(self, func, *args, **kwargs):
        """
        Set a callback function to be run after the VCS action has ran.
        The actual function is called from the self.run() method.
        
        @type   func: function
        @param  func: The function to run after the VCS action has ran.
        
        """
        
        self.post_func = func
        self.post_args = args
        self.post_kwargs = kwargs
    
    def set_action(self, func, *args, **kwargs):
        """
        Set the callback function to be run as the main VCS action.
        The actual function is called from the self.run() method.
        
        @type   func: function
        @param  func: The function to be run as the main VCS action.
        
        """

        self._func = func
        self._args = args
        self._kwargs = kwargs
     
    def run(self):
        """
        The central method that drives this class.  It runs the before and 
        after methods, as well as the main vcs method.
        
        """
        
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

