#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.view

class Log:
    def __init__(self):
        self.view = component.view.InterfaceView(self, "Log")

        self.revisions_table = component.widget.Table(
            self.view.get_widget("log_revisions_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Revision", "Author", 
                "Date", "Message"]
        )
        self.revisions = [
            ["100", "Adam Plumb", "2008-10-20 22:12:23", "This is a message"],
            ["98", "Adam Plumb", "2008-10-12 22:12:23", "This is another message"]
        ]
        for row in self.revisions:
            self.revisions_table.append(row)

        self.paths_table = component.widget.Table(
            self.view.get_widget("log_paths_table"),
            [gobject.TYPE_STRING, gobject.TYPE_STRING], 
            ["Action", "Path"]
        )
        self.paths = [
            ["Added", "test.html"],
            ["Committed", "index.html"]
        ]
        for row in self.paths:
            self.paths_table.append(row)

        self.message = component.widget.TextView(
            self.view.get_widget("log_message")
        )

        self.progress_bar = self.view.get_widget("log_progress_bar")
        self.progress_bar.set_fraction(.3)

    def on_log_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_log_cancel_clicked(self, widget, data=None):
        gtk.main_quit()
        
    def on_log_ok_clicked(self, widget, data=None):
        print "OK"
        
    def on_log_revisions_table_button_pressed(self, treeview, event):
        pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
        if pathinfo is not None:
            path, col, cellx, celly = pathinfo

            #treeview.grab_focus()
            #treeview.set_cursor(path, col, 0)
            
            selection = treeview.get_selection()
            rows = selection.get_selected_rows()
            
            if path not in rows[1]:
                selection.unselect_all()
                selection.select_path(path)
            
            if selection.count_selected_rows() == 1:
                self.message.set_text(treeview.get_model()[path][3])
        return True
        
if __name__ == "__main__":
    window = Log()
    gtk.main()
