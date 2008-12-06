import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.notification

class Add:

    TOGGLE_ALL = False

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "add", "Add")

        self.files_table = nautilussvn.ui.widget.Table(
            self.view.get_widget("files_table"), 
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [nautilussvn.ui.widget.TOGGLE_BUTTON, "Path", "Extension"]
        )

        self.files = [
            [False, "ADDEDLATER.jpg", "jpg"],
            [True, "ADDEDLATER2.jpg", "jpg"]
        ]
        for row in self.files:
            self.files_table.append(row)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_select_all_toggled(self, widget):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.files_table.get_items():
            row[0] = self.TOGGLE_ALL

    def on_files_table_button_pressed(self, treeview, event=None, user_data=None):
        if event.button == 3:
            pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                
                treeview_model = treeview.get_model()
                fileinfo = treeview_model[path]
                
                context_menu = nautilussvn.ui.widget.ContextMenu([{
                        'label': 'View Diff',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_diff_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
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
                
    def on_files_table_row_doubleclicked(self, treeview, event, col):
        treeview.grab_focus()
        treeview.set_cursor(event[0], col, 0)
        treeview_model = treeview.get_model()
        fileinfo = treeview_model[event[0]]
        
        print "Row Double-clicked"
                
    def on_context_open_activated(self, widget, Data=None):
        print "Open Item"

    def on_context_diff_activated(self, widget, Data=None):
        print "Diff Item"
        
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
