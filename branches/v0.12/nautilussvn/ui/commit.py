#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.dialog
import component.view

class Commit:

    TOGGLE_ALL = True
    SHOW_UNVERSIONED = True

    def __init__(self):
        self.view = component.view.InterfaceView(self, "Commit")

        self.files_table = component.widget.Table(
            self.view.get_widget("commit_files_table"),
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [component.widget.TOGGLE_BUTTON, "Path", "Extension", 
                "Text Status", "Property Status"],
        )
        
        self.files = [
            [True, "test.php", ".php", "modified", ""],
            [False, "added.php", ".php", "unversioned", ""]
        ]
        self.populate_files_from_original()
        
        self.message = component.widget.TextView(
            self.view.get_widget("commit_message")
        )
    
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
                context_menu = component.widget.ContextMenu([{
                        'label': 'Open',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_open_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Browse',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_browse_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Delete',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_delete_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Add',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_add_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Add to ignore list',
                        'submenu': [{
                                'label': fileinfo[1],
                                'signals': {
                                    'activate': {
                                        'callback':self.on_subcontext_ignore_by_filename_activated, 
                                        'args':fileinfo
                                     }
                                 }
                            },
                            {
                                'label': "*.%s"%fileinfo[2],
                                'signals': {
                                    'activate': {
                                        'callback':self.on_subcontext_ignore_by_fileext_activated, 
                                        'args':fileinfo
                                    }
                                }
                            }
                        ]
                    }
                ])
                context_menu.show(event)

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
        dialog = component.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
        
if __name__ == "__main__":
    window = Commit()
    gtk.main()
