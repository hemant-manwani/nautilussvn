import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.notification

class Rename:
    def __init__(self, filename=""):
        self.view = nautilussvn.ui.InterfaceView(self, "rename", "Rename")
        self.view.get_widget("new_name").set_text(filename)
        
    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        self.view.hide()
        self.notification = nautilussvn.ui.notification.Notification()
        
if __name__ == "__main__":
    window = Rename("test.txt")
    gtk.main()
