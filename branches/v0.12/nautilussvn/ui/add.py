#!/usr/bin/env python

import pygtk
import gobject
import gtk

import widgets
import views

class Add:

    TOGGLE_ALL = True

    def __init__(self):
        self.view = views.InterfaceView(self, "Add")

        self.add_files_table = widgets.Table(
            self.view.get_widget("add_files_table"), 
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [widgets.TOGGLE_BUTTON, "Path", "Extension"]
        )

        self.files = [
            [False, "ADDEDLATER.jpg", "jpg"],
            [True, "ADDEDLATER2.jpg", "jpg"]
        ]
        for row in self.files:
            self.add_files_table.append(row)

    def on_add_destroy(self, widget):
        gtk.main_quit()

    def on_add_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_add_ok_clicked(self, widget):
        print "OK"

    def on_add_toggle_toggled(self, widget):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.add_files_table.get_items():
            row[0] = self.TOGGLE_ALL

    def on_add_files_table_button_pressed(self, treeview, event):
        if event.button == 3:
            pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                
                treeview_model = treeview.get_model()
                fileinfo = treeview_model[path]
                
                contextMenu = gtk.Menu()
                openItem = gtk.MenuItem("Open")
                openItem.connect('activate', self.on_context_open_item_activated, fileinfo)
                contextMenu.add(openItem)
                
                browseItem = gtk.MenuItem("Browse to")
                browseItem.connect('activate', self.on_context_browse_item_activated, fileinfo)
                contextMenu.add(browseItem)
                
                delItem = gtk.MenuItem("Delete")
                delItem.connect('activate', self.on_context_delete_item_activated, fileinfo)
                contextMenu.add(delItem)
                
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
                
    def on_context_open_item_activated(self, widget, Data=None):
        print "Open Item"
        
    def on_context_browse_item_activated(self, widget, Data=None):
        print "Browse Item"

    def on_context_delete_item_activated(self, widget, Data=None):
        print "Delete Item"
        
    def on_subcontext_ignore_by_filename_activated(self, widget, Data=None):
        print "Ignore by file name"
        
    def on_subcontext_ignore_by_fileext_activated(self, widget, Data=None):
        print "Ignore by file extension"
        
if __name__ == "__main__":
    window = Add()
    gtk.main()
