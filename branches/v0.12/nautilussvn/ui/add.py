#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.view

class Add:

    TOGGLE_ALL = True

    def __init__(self):
        self.view = component.view.InterfaceView(self, "Add")

        self.add_files_table = component.widget.Table(
            self.view.get_widget("add_files_table"), 
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [component.widget.TOGGLE_BUTTON, "Path", "Extension"]
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
                
    def on_context_open_activated(self, widget, Data=None):
        print "Open Item"
        
    def on_context_browse_activated(self, widget, Data=None):
        print "Browse Item"

    def on_context_delete_activated(self, widget, Data=None):
        print "Delete Item"
        
    def on_subcontext_ignore_by_filename_activated(self, widget, Data=None):
        print "Ignore by file name"
        
    def on_subcontext_ignore_by_fileext_activated(self, widget, Data=None):
        print "Ignore by file extension"
        
if __name__ == "__main__":
    window = Add()
    gtk.main()
