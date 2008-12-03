#!/usr/bin/env python

import pygtk
import gobject
import gtk

import component.widget
import component.view
import component.helper

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
        self.revisions_table.allow_multiple()
        
        self.revisions = [
            ["100", "Adam Plumb", "2008-10-20 22:12:23", "This is a message"],
            ["97", "Adam Plumb", "2008-10-12 22:12:23", "This is another message"],
            ["96", "Bruce", "2008-10-05 22:12:23", "Earlier log message"],
            ["95", "Bruce", "2008-10-01 22:12:23", "did this did that"]
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

    def on_log_revisions_table_button_released(self, treeview, event):
        path = treeview.get_path_at_pos(int(event.x), int(event.y))
        
        if path is not None:
            selection = treeview.get_selection()
            self.selected_rows = selection.get_selected_rows()

            if selection.count_selected_rows() == 1:
                self.message.set_text(self.selected_rows[0][path[0]][3])
            else:
                self.message.set_text("")
                
    def get_selected_revision_numbers(self):
        returner = []
        for row in self.selected_rows[0]:
            returner.append(int(row[0]))
        
        returner.sort()
        return component.helper.encode_revisions(returner)
            
        
      
if __name__ == "__main__":
    window = Log()
    gtk.main()
