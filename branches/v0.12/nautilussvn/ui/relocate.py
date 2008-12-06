import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.notification

import nautilussvn.lib.helper

class Relocate:
    """
    Interface to relocate your working copy's repository
    
    """

    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "relocate", "Relocate")

        self.repositories = nautilussvn.ui.widget.ComboBox(
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

if __name__ == "__main__":
    window = Relocate()
    gtk.main()
