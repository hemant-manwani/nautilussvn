import os.path
from os.path import isdir
import re
import urllib
from subprocess import Popen

import nautilus

class OpenTerminalExtension(nautilus.MenuProvider):

    def __init__(self):
        pass

    def get_file_items(self, window, items):
        if len(items) == 0: return
        item = items[0]

        menu_item = nautilus.MenuItem(
            "OpenTerminal::OpenTerminal",
            "Open In Terminal",
            "",
            "gnome-terminal"
        )

        def open_terminal(menu_item):
            """
            Ignore the ugliness, quick hack.
            """
            uri = urllib.unquote(item.get_uri())
            
            if item.get_uri().startswith("x-nautilus-desktop://"):
                Popen(["gnome-terminal", "--working-directory", "%s/Desktop" % os.path.expanduser("~")]).pid
            elif item.get_uri().startswith("file://"):
                path = uri.replace("file://", "")
                if not isdir(path): path = os.path.dirname(path)
                Popen(["gnome-terminal", "--working-directory", path]).pid
            elif item.get_uri().startswith("sftp://"):
                hostname, path = re.match("sftp://([^/]+)(/.*)", uri).groups()
                dirname = os.path.dirname(path) # might have selected a file
                ssh_command = 'ssh %s -t \'cd "%s" || cd "%s"; $SHELL -l\'' % (hostname, path, dirname)
                Popen(["gnome-terminal", "-e", ssh_command]).pid

        menu_item.connect("activate", open_terminal)

        return [menu_item]


    def get_background_items(self, window, item):
        return self.get_file_items(window, [item])

