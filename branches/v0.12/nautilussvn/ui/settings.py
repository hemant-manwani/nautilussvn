import os

import pygtk
import gobject
import gtk

import nautilussvn.ui
import nautilussvn.ui.widget
import nautilussvn.ui.dialog
import nautilussvn.lib.settings
import nautilussvn.lib.helper

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
    
    def on_external_diff_tool_browse_clicked(self, widget):
        chooser = nautilussvn.ui.dialog.FileChooser(
            "Select a program", "/usr/bin"
        )
        path = chooser.run()
        path = path.replace("file://", "")
        if path is not None:
            self.view.get_widget("diff_tool").set_text(path)

    def on_external_repo_browser_browse_clicked(self, widget):
        chooser = nautilussvn.ui.dialog.FileChooser(
            "Select a program", "/usr/bin"
        )
        path = chooser.run()
        path = path.replace("file://", "")
        if path is not None:
            self.view.get_widget("repo_browser").set_text(path)

    def on_cache_clear_repositories_clicked(self, widget):
        path = nautilussvn.lib.helper.get_repository_paths_path()
        fh = open(path, "w")
        fh.write("")
        fh.close()

    def on_cache_clear_messages_clicked(self, widget):
        path = nautilussvn.lib.helper.get_previous_messages_path()
        fh = open(path, "w")
        fh.write("")
        fh.close()

    def on_cache_clear_authentication_clicked(self, widget):
        pass
        
if __name__ == "__main__":
    window = Settings()
    gtk.main()
