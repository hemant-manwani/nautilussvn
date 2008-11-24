#!/usr/bin/env python

import pygtk
import gobject
import gtk

import widget
import dialog
import view

class Commit:

    TOGGLE_ALL = True
    SHOW_UNVERSIONED = True

    def __init__(self):
        self.view = view.InterfaceView(self, "Commit")

        self.files_table = widget.Table(
            self.view.get_widget("commit_files_table"),
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [widget.TOGGLE_BUTTON, "Path", "Extension", "Text Status", "Property Status"],
        )
        
        self.files = [
            [True, "test.php", ".php", "modified", ""],
            [False, "added.php", ".php", "unversioned", ""]
        ]
        self.populate_files_from_original()
        
        self.message = widget.TextView(self.view.get_widget("commit_message"))
    
    def on_commit_destroy(self, widget):
        gtk.main_quit()
        
    def on_commit_cancel_clicked(self, widget, data=None):
        gtk.main_quit()
        
    def on_commit_ok_clicked(self, widget, data=None):
        print "OK"
    
    def on_commit_toggle_show_all_toggled(self, widget, data=None):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.files_table.get_items():
            row[0] = self.TOGGLE_ALL
            
    def on_commit_toggle_show_unversioned_toggled(self, widget, data=None):
        self.SHOW_UNVERSIONED = not self.SHOW_UNVERSIONED

        if self.SHOW_UNVERSIONED:
            self.populate_files_from_original()
        else:
            index = 0
            for row in self.files_table.get_items():
                if row[3] == "unversioned":
                    self.files_table.remove(index)
                index += 1

    def populate_files_from_original(self):
        self.files_table.clear()
        for row in self.files:
            self.files_table.append(row)
        
    def on_commit_files_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            treeview_model = treeview.get_model()
            fileinfo = treeview_model[path]
            
            if event.button == 3:
                contextMenu = gtk.Menu()
                
                openItem = gtk.MenuItem("Open")
                openItem.connect('activate', self.on_context_open_activated, fileinfo)
                contextMenu.add(openItem)
                
                browseItem = gtk.MenuItem("Browse to")
                browseItem.connect('activate', self.on_context_browse_activated, fileinfo)
                contextMenu.add(browseItem)
                
                delItem = gtk.MenuItem("Delete")
                delItem.connect('activate', self.on_context_delete_activated, fileinfo)
                contextMenu.add(delItem)

                addItem = gtk.MenuItem("Add")
                addItem.connect('activate', self.on_context_add_activated, fileinfo)
                contextMenu.add(addItem)
                
                ignoreSubMenu = gtk.Menu()
                
                ignoreByFileName = gtk.MenuItem(fileinfo[1])
                ignoreByFileName.connect('activate', self.on_subcontext_ignore_by_filename_activated, fileinfo)
                ignoreSubMenu.add(ignoreByFileName)
                
                ignoreByFileExt = gtk.MenuItem("*.%s"%fileinfo[2])
                ignoreByFileExt.connect('activate', self.on_subcontext_ignore_by_fileext_activated, fileinfo)
                ignoreSubMenu.add(ignoreByFileExt)
                
                ignoreItem = gtk.MenuItem("Add to ignore list")
                ignoreItem.set_submenu(ignoreSubMenu)
                contextMenu.add(ignoreItem)
                
                contextMenu.show_all()
                contextMenu.popup(None, None, None, event.button, event.time)

    def on_context_add_activated(self, widget, data=None):
        print "Add Item"

    def on_context_open_activated(self, widget, data=None):
        print "Open Item"
        
    def on_context_browse_activated(self, widget, data=None):
        print "Browse Item"

    def on_context_delete_activated(self, widget, data=None):
        print "Delete Item"
        
    def on_subcontext_ignore_by_filename_activated(self, widget, data=None):
        print "Ignore by file name"
        
    def on_subcontext_ignore_by_fileext_activated(self, widget, data=None):
        print "Ignore by file extension"
        
    def on_commit_previous_messages_clicked(self, widget, data=None):
        dialog = dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
        
if __name__ == "__main__":
    window = Commit()
    gtk.main()
