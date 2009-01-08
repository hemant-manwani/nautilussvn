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

import pygtk
import gobject
import gtk

from nautilussvn.ui import InterfaceView
from nautilussvn.ui.log import LogDialog
import nautilussvn.ui.widget
import nautilussvn.lib.helper

class Merge(InterfaceView):
    def __init__(self, path):
        InterfaceView.__init__(self, "merge2", "Merge")
        self.assistant = self.get_widget("Merge")
        
        self.path = path
        
        self.page = self.assistant.get_nth_page(0)
        
        self.assistant.set_page_complete(self.page, True)
        self.assistant.set_forward_page_func(self.on_forward_clicked)
        
        self.repo_paths = nautilussvn.lib.helper.get_repository_paths()
        
        # Keeps track of which stages should be marked as complete
        self.stages = {
            0: True,
            1: False,
            2: False,
            3: False,
            4: False
        }
    #
    # Assistant UI Signal Callbacks
    #

    def on_destroy(self, widget):
        self.close()
    
    def on_cancel_clicked(self, widget):
        self.close()
    
    def on_close_clicked(self, widget):
        self.close()

    def on_apply_clicked(self, widget):
        self.close()

    def on_prepare(self, widget, page):
        self.page = page
        
        current = self.assistant.get_current_page()
        if current == 1:
            self.on_mergerange_prepare()
        elif current == 2:
            self.on_mergebranch_prepare()
        elif current == 3:
            self.on_mergetree_prepare()
        elif current == 4:
            self.on_mergeoptions_prepare()

    def on_forward_clicked(self, widget):
        current = self.assistant.get_current_page()
        if current == 0:
            if self.get_widget("mergetype_range_opt").get_active():
                next = 1
            elif self.get_widget("mergetype_reintegrate_opt").get_active():
                next = 2
            elif self.get_widget("mergetype_tree_opt").get_active():
                next = 3
        else:
            next = 4
        
        return next

    #
    # Step 2a: Merge a Range of Revisions
    #
    
    def on_mergerange_prepare(self):
        self.mergerange_repos = nautilussvn.ui.widget.ComboBox(
            self.get_widget("mergerange_from_urls"), 
            self.repo_paths
        )
        self.get_widget("mergerange_working_copy").set_text(self.path)
        
    def on_mergerange_show_log1_clicked(self, widget):
        LogDialog(
            self.path,
            ok_callback=self.on_mergerange_log1_closed, 
            multiple=True
        )
    
    def on_mergerange_log1_closed(self, data):
        self.get_widget("mergerange_revisions").set_text(data)
    
    def on_mergerange_show_log2_clicked(self, widget):
        LogDialog(self.path)

    def on_mergerange_from_url_changed(self, widget):
        self.mergerange_check_ready()

    def on_mergerange_revisions_changed(self, widget):
        self.mergerange_check_ready()

    def mergerange_check_ready(self):
        ready = True
        if self.get_widget("mergerange_from_url").get_text() == "":
            ready = False
        if self.get_widget("mergerange_revisions").get_text() == "":
            ready = False

        self.assistant.set_page_complete(self.page, ready)

    #
    # Step 2b: Reintegrate a Branch
    #

    def on_mergebranch_prepare(self):
        self.mergebranch_repos = nautilussvn.ui.widget.ComboBox(
            self.get_widget("mergebranch_from_urls"), 
            self.repo_paths
        )
        self.get_widget("mergebranch_working_copy").set_text(self.path)

    def on_mergebranch_show_log1_clicked(self, widget):
        LogDialog(self.path)

    def on_mergebranch_show_log2_clicked(self, widget):
        LogDialog(self.path)
        
    def on_mergebranch_from_url_changed(self, widget):
        self.mergebranch_check_ready()
    
    def mergebranch_check_ready(self):
        ready = True
        if self.get_widget("mergebranch_from_url").get_text() == "":
            ready = False

        self.assistant.set_page_complete(self.page, ready)

    #
    # Step 2c: Merge two different trees
    #
    
    def on_mergetree_prepare(self):
        self.mergetree_from_repos = nautilussvn.ui.widget.ComboBox(
            self.get_widget("mergetree_from_urls"), 
            self.repo_paths
        )
        self.mergetree_to_repos = nautilussvn.ui.widget.ComboBox(
            self.get_widget("mergetree_to_urls"), 
            self.repo_paths
        )
        self.get_widget("mergetree_working_copy").set_text(self.path)

    def on_mergetree_from_show_log_clicked(self, widget):
        LogDialog(
            self.path,
            ok_callback=self.on_mergetree_from_show_log_closed, 
            multiple=False
        )

    def on_mergetree_from_show_log_closed(self, data):
        self.get_widget("mergetree_from_revision_number").set_text(data)
        self.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_show_log_clicked(self, widget):
        LogDialog(
            self.path,
            ok_callback=self.on_mergetree_to_show_log_closed, 
            multiple=False
        )

    def on_mergetree_to_show_log_closed(self, data):
        self.get_widget("mergetree_to_revision_number").set_text(data)
        self.get_widget("mergetree_to_revision_number_opt").set_active(True)

    def on_mergetree_working_copy_show_log_clicked(self, widget):
        LogDialog(self.path)
        
    def on_mergetree_from_revision_number_focused(self, widget, data):
        self.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_revision_number_focused(self, widget, data):
        self.get_widget("mergetree_to_revision_number_opt").set_active(True)

    def on_mergetree_from_url_changed(self, widget):
        self.mergetree_check_ready()

    def on_mergetree_to_url_changed(self, widget):
        self.mergetree_check_ready()

    def mergetree_check_ready(self):
        ready = True
        if self.get_widget("mergetree_from_url").get_text() == "":
            ready = False
        if self.get_widget("mergetree_to_url").get_text() == "":
            ready = False

        self.assistant.set_page_complete(self.page, ready)
 
    #
    # Step 3: Merge Options
    #
    
    def on_mergeoptions_prepare(self):
        DEPTHS = {
            'a': 'Working Copy',
            'b': 'Fully recursive',
            'c': 'Immediate children, including folders',
            'd': 'Only file children',
            'e': 'Only this item'
        }
        self.depth = nautilussvn.ui.widget.ComboBox(
            self.get_widget("mergeoptions_depth")
        )
        for i in DEPTHS.values():
            self.depth.append(i)
        self.depth.set_active(0)

    def on_mergeoptions_test_merge_clicked(self, widget):
        print "Test Merge"

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python %s [path]" % __file__)
    window = Merge(args[0])
    window.register_gtk_quit()
    gtk.main()
