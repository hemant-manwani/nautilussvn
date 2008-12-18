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

import nautilussvn.ui.dialog
import nautilussvn.ui.notification
import nautilussvn.lib.helper

STEP2 = None

class MergeType:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "merge", "MergeType")

    def on_mergetype_destroy(self, widget):
        gtk.main_quit()

    def on_mergetype_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergetype_forward_clicked(self, widget):
        self.view.hide()
        
        if self.view.get_widget("mergetype_range_opt").get_active():
            STEP2 = MergeRange(self)
        elif self.view.get_widget("mergetype_reintegrate_opt").get_active():
            STEP2 = MergeBranch(self)
        elif self.view.get_widget("mergetype_tree_opt").get_active():
            STEP2 = MergeTree(self)
            
        STEP2.view.show()

class MergeRange:
    """
    Provides an interface for the Merge Wizard Step 2a (Range of Revisions)
    """
    def __init__(self, parent):
        self.view = nautilussvn.ui.InterfaceView(self, "merge", "MergeRange")
        self.parent = parent
        
        self.repositories = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("mergerange_from_urls"), 
            nautilussvn.lib.helper.get_repository_paths()
        )

    def on_mergerange_destroy(self, widget):
        gtk.main_quit()

    def on_mergerange_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergerange_back_clicked(self, widget):
        self.view.hide()
        self.parent.view.show()

    def on_mergerange_forward_clicked(self, widget):
        self.view.hide()
        self.options = MergeOptions(self)
        self.options.view.show()
        
    def on_mergerange_show_log1_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_log1_closed, multiple=True)
    
    def on_log1_closed(self, data):
        self.view.get_widget("mergerange_revisions").set_text(data)
    
    def on_mergerange_show_log2_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog()
        
class MergeBranch:
    """
    Provides an interface for the Merge Wizard Step 2b (Reintegrate Branch)
    """
    def __init__(self, parent):
        self.view = nautilussvn.ui.InterfaceView(self, "merge", "MergeBranch")
        self.parent = parent

        self.repositories = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("mergebranch_from_urls"), 
            nautilussvn.lib.helper.get_repository_paths()
        )

    def on_mergebranch_destroy(self, widget):
        gtk.main_quit()

    def on_mergebranch_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergebranch_back_clicked(self, widget):
        self.view.hide()
        self.parent.view.show()

    def on_mergebranch_forward_clicked(self, widget):
        self.view.hide()
        self.options = MergeOptions(self)
        self.options.view.show()
        
    def on_mergebranch_show_log1_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog()

    def on_mergebranch_show_log2_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog()

class MergeTree:
    """
    Provides an interface for the Merge Wizard Step 2c (Merge two trees)
    """
    def __init__(self, parent):
        self.view = nautilussvn.ui.InterfaceView(self, "merge", "MergeTree")
        self.parent = parent

        previous_urls = nautilussvn.lib.helper.get_repository_paths()
        self.from_urls = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("mergetree_from_urls"), 
            previous_urls
        )
        self.to_urls = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("mergetree_to_urls"), 
            previous_urls
        )

    def on_mergetree_destroy(self, widget):
        gtk.main_quit()

    def on_mergetree_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergetree_back_clicked(self, widget):
        self.view.hide()
        self.parent.view.show()

    def on_mergetree_forward_clicked(self, widget):
        self.view.hide()
        self.options = MergeOptions(self)
        self.options.view.show()
        
    def on_mergetree_from_show_log_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_from_show_log_closed, multiple=False)

    def on_from_show_log_closed(self, data):
        self.view.get_widget("mergetree_from_revision_number").set_text(data)
        self.view.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_show_log_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog(ok_callback=self.on_to_show_log_closed, multiple=False)

    def on_to_show_log_closed(self, data):
        self.view.get_widget("mergetree_to_revision_number").set_text(data)
        self.view.get_widget("mergetree_to_revision_number_opt").set_active(True)

    def on_mergetree_working_copy_show_log_clicked(self, widget):
        nautilussvn.ui.dialog.LogDialog()
        
    def on_mergetree_from_revision_number_focused(self, widget, data):
        self.view.get_widget("mergetree_from_revision_number_opt").set_active(True)

    def on_mergetree_to_revision_number_focused(self, widget, data):
        self.view.get_widget("mergetree_to_revision_number_opt").set_active(True)

class MergeOptions:
    """
    Provides an interface for the Merge Wizard Step 3 (Options)
    """

    DEPTHS = {
        'a': 'Working Copy',
        'b': 'Fully recursive',
        'c': 'Immediate children, including folders',
        'd': 'Only file children',
        'e': 'Only this item'
    }

    def __init__(self, parent):
        self.view = nautilussvn.ui.InterfaceView(self, "merge", "MergeOptions")
        self.parent = parent
        
        self.depth = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("mergeoptions_depth")
        )
        for i in self.DEPTHS.values():
            self.depth.append(i)
        self.depth.set_active(0)
        
    def on_mergeoptions_destroy(self, widget):
        gtk.main_quit()

    def on_mergeoptions_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_mergeoptions_back_clicked(self, widget):
        self.view.hide()
        self.parent.view.show()

    def on_mergeoptions_apply_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()
        
    def on_mergeoptions_test_merge_clicked(self, widget):
        self.view.hide()

if __name__ == "__main__":
    window = MergeType()
    gtk.main()
