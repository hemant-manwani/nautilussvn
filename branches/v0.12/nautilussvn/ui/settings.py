import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget

class Settings:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "settings", "Settings")

        self.language = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("general_language"), 
            ['English']
        )
        self.language.set_active(0)

    def on_destroy(self, widget):
        gtk.main_quit()

    def on_cancel_clicked(self, widget):
        gtk.main_quit()

    def on_ok_clicked(self, widget):
        gtk.main_quit()
    
    def on_apply_clicked(self, widget):
        gtk.main_quit()

if __name__ == "__main__":
    window = Settings()
    gtk.main()
