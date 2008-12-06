import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.ui.notification

class Lock:

    TOGGLE_ALL = False

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "lock", "Lock")

        self.files_table = nautilussvn.ui.widget.Table(
            self.view.get_widget("files_table"),
            [gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            [nautilussvn.ui.widget.TOGGLE_BUTTON, "Path", "Extension", 
                "Lock", "Needs lock"],
        )
        
        self.files = [
            [True, "init/test.php", ".php", "", ""],
            [False, "added.php", ".php", "", ""]
        ]
        self.files_table.clear()
        for row in self.files:
            self.files_table.append(row)
        
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )
    
    def on_destroy(self, widget):
        gtk.main_quit()
        
    def on_cancel_clicked(self, widget, data=None):
        gtk.main_quit()
        
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()
    
    def on_select_all_toggled(self, widget, data=None):
        self.TOGGLE_ALL = not self.TOGGLE_ALL
        for row in self.files_table.get_items():
            row[0] = self.TOGGLE_ALL

    def on_files_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
            treeview_model = treeview.get_model()
            fileinfo = treeview_model[path]
            
            if event.button == 3:
                context_menu = nautilussvn.ui.widget.ContextMenu([{
                        'label': 'Compare with base',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_diff_activated, 
                                'args':fileinfo
                            }
                        }
                    },{
                        'label': 'Show log',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_show_log_activated, 
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
                        'label': 'Properties',
                        'signals': {
                            'activate': {
                                'callback':self.on_context_properties_activated, 
                                'args':fileinfo
                            }
                        }
                    }
                ])
                context_menu.show(event)

    def on_files_table_row_doubleclicked(self, treeview, event, col):
        treeview.grab_focus()
        treeview.set_cursor(event[0], col, 0)
        treeview_model = treeview.get_model()
        fileinfo = treeview_model[event[0]]
        
        print "Row Double-clicked"

    def on_context_show_log_activated(self, widget, data=None):
        print "Show log Item"

    def on_context_diff_activated(self, widget, Data=None):
        print "Diff Item"

    def on_context_open_activated(self, widget, data=None):
        print "Open Item"
        
    def on_context_browse_activated(self, widget, data=None):
        print "Browse Item"

    def on_context_delete_activated(self, widget, data=None):
        print "Delete Item"
        
    def on_context_properties_activated(self, widget, data=None):
        print "Properties Item"
        
    def on_previous_messages_clicked(self, widget, data=None):
        dialog = nautilussvn.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
        
if __name__ == "__main__":
    window = Lock()
    gtk.main()
