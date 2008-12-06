import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.log
import nautilussvn.ui.notification

class Update:
    """
    This class provides an interface to generate an "update".
    Pass it a path and it will start an update, running the notification dialog.  
    There is no glade view.
    
    """

    def __init__(self):
        self.notification = nautilussvn.ui.notification.Notification()


class UpdateToRevision:
    """
    This class provides an interface to update a working copy to a specific
    revision.  It has a glade view.
    
    """
    
    DEPTHS = {
        'a': 'Working Copy',
        'b': 'Fully recursive',
        'c': 'Immediate children, including folders',
        'd': 'Only file children',
        'e': 'Only this item'
    }
    
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "update", "Update")
        
        self.depth = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("depth")
        )
        for i in self.DEPTHS.values():
            self.depth.append(i)
        self.depth.set_active(0)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()

    def on_revision_number_focused(self, widget, data=None):
        self.view.get_widget("revision_number_opt").set_active(True)

    def on_show_log_clicked(self, widget, data=None):
        LogForUpdate(ok_clicked=self.on_log_closed)
    
    def on_log_closed(self, data):
        if data is not None:
            self.view.get_widget("revision_number_opt").set_active(True)
            self.view.get_widget("revision_number").set_text(data)

class LogForUpdate(nautilussvn.ui.log.Log):
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
    window = UpdateToRevision()
    gtk.main()
