import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.notification

class Export:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "export", "Export")

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()
        
if __name__ == "__main__":
    window = Export()
    gtk.main()
