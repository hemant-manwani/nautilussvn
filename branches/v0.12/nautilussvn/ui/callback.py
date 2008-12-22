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

import nautilussvn.ui.notification
import nautilussvn.ui.dialog
import nautilussvn.lib.vcs

class VCSCallbacks:
    """
    Provides a central interface to handle vcs callbacks.
    Loads UI elements that require user interaction.
    
    """
    
    def __init__(self, client):
        
        self.client = client
        
        self.client.set_callback_cancel(self.cancel)
        self.client.set_callback_notify(self.notify)
        self.client.set_callback_get_log_message(self.get_log_message)
        self.client.set_callback_get_login(self.get_login)
        self.client.set_callback_ssl_server_trust_prompt(self.get_ssl_trust)
        self.client.set_callback_ssl_client_cert_password_prompt(self.get_ssl_password)
        
        self.notification = nautilussvn.ui.notification.Notification()
        
    def cancel(self):
        return True
    
    def notify(self, data):
        self.notification.append([
            self.client.NOTIFY_ACTIONS[data["action"]],
            data["path"],
            data["mime_type"]
        ])
        
        if data["action"] in self.client.NOTIFY_ACTIONS_COMPLETE:
            self.finish()
    
    def finish(self):
        self.notification.view.get_widget("ok").set_sensitive(True)
    
    def get_log_message(self):
        return True, "Empty Message"
    
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
