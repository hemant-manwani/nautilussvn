import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.dialog
import nautilussvn.ui.widget
import nautilussvn.ui.notification
import nautilussvn.ui.log

import nautilussvn.lib.helper

class Branch:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "branch", "Branch")
        self.message = nautilussvn.ui.widget.TextView(
            self.view.get_widget("message")
        )
        self.urls = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("to_urls"), 
            nautilussvn.lib.helper.GetRepositoryPaths()
        )

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_from_revision_number_focused(self, widget, data=None):
        self.view.get_widget("from_revision_number_opt").set_active(True)

    def on_previous_messages_clicked(self, widget, data=None):
        dialog = nautilussvn.ui.dialog.PreviousMessages()
        message = dialog.run()
        if message is not None:
            self.message.set_text(message)
            
    def on_show_log_clicked(self, widget, data=None):
        LogForCopy(ok_clicked=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("from_revision_number_opt").set_active(True)
            self.view.get_widget("from_revision_number").set_text(data)

class LogForCopy(nautilussvn.ui.log.Log):
    def __init__(self, ok_clicked=None):
        nautilussvn.ui.log.Log.__init__(self)
        self.ok_clicked = ok_clicked
        
    def on_destroy(self, widget):
        self.view.hide()
    
    def on_cancel_clicked(self, widget, data=None):
        self.view.hide()
    
    def on_ok_clicked(self, widget, data=None):
        self.view.hide()
        if self.ok_clicked is not None:
            self.ok_clicked(self.get_selected_revision_number())

if __name__ == "__main__":
    window = Branch()
    gtk.main()
