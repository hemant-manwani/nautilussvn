import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.lib.settings

class Settings:
    def __init__(self):
        self.view = nautilussvn.ui.InterfaceView(self, "settings", "Settings")

        self.settings = nautilussvn.lib.settings.SettingsManager()
        
        self.language = nautilussvn.ui.widget.ComboBox(
            self.view.get_widget("language"), 
            ['English']
        )
        self.language.set_active_from_value(
            self.settings.get("general", "language")
        )
        self.view.get_widget("enable_attributes").set_active(
            int(self.settings.get("general", "enable_attributes"))
        )
        self.view.get_widget("enable_emblems").set_active(
            int(self.settings.get("general", "enable_emblems"))
        )
        self.view.get_widget("enable_recursive").set_active(
            int(self.settings.get("general", "enable_recursive"))
        )
        self.view.get_widget("diff_tool").set_text(
            self.settings.get("external", "diff_tool")
        )
        self.view.get_widget("diff_tool_swap").set_active(
            int(self.settings.get("external", "diff_tool_swap"))
        )
        self.view.get_widget("repo_browser").set_text(
            self.settings.get("external", "repo_browser")
        )
        self.view.get_widget("cache_number_repositories").set_text(
            self.settings.get("cache", "number_repositories")
        )
        self.view.get_widget("cache_number_messages").set_text(
            self.settings.get("cache", "number_messages")
        )
        
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
