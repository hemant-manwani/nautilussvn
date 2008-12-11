import os

import shutil
import configobj

import nautilussvn.lib.helper

MAIN_SETTINGS_FILE = "%s/settings.conf" % nautilussvn.lib.helper.get_home_folder()

DEFAULT_SETTINGS = {
    "general": {
        "language": "English"
    },
    "external": {
        "diff_files_tool": "/usr/bin/meld",
        "diff_files_swap": False,
        "diff_props_tool": "/usr/bin/meld",
        "diff_props_swap": False,
        "merge_tool": "/usr/bin/meld",
        "repo_browser": "firefox"
    }
}

class SettingsManager:
    """
    This class provides an shallow interface for the rest of the program to use 
    to interact with our configuration file.
    
    Usage:
        Get settings:
            sm = SettingsManager()
            diff_tool = sm.get("external", "diff_tool")
        Set settings:
            sm = SettingsManager()
            sm.set("external", "diff_tool", "/usr/bin/meld")
    """
    
    def __init__(self):
    
        if not os.path.exists(MAIN_SETTINGS_FILE):
            self.use_default_settings()
    
        self.settings = configobj.ConfigObj(
            MAIN_SETTINGS_FILE, 
            indent_type="    "
        )

    def get(self, section=None, keyword=None):
        """
        Get the settings for a section and/or keyword
        If no arguments are given, it just returns all settings
        
        @type section:  string
        @param section: a settings section
        
        @type keyword:  string
        @param keyword: a particular setting in a section
        
        @rtype dict or string
        @return either a dict or string with setting(s)
        
        """
        
        if section is None:
            return self.settings
            
        if keyword is None:
            return self.settings[section]
        
        returner = None
        try:
            returner = self.settings[section][keyword]
        except KeyError:
            print "Error: section %s:%s doesn't exist" % (section, keyword)
            
        return returner
        
    def set(self, section, keyword, value=""):
        """
        Set settings for a particular section and keyword

        @type section:  string
        @param section: a settings section
        
        @type keyword:  string
        @param keyword: a particular setting in a section
        
        @type value:    string or dict
        @param value:   setting value

        """
        
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][keyword] = value
            
    def set_comments(self, section, comments=[]):
        """
        Set multi-line comments for a section
        
        @type section:  string
        @param section: a settings section
        
        @type comments: list
        @param comments:a list of strings
        
        """

        self.settings.comments[section] = comments
        
    def set_inline_comments(self, section, comments=""):
        """
        Set inline comments for a section
        
        @type section:  string
        @param section: a settings section
        
        @type comments: string
        @param comments:a single line comment
        
        """

        self.settings.inline_comments[section] = comments
        
    def write(self):
        """
        Write the settings and comments to the settings file
        
        """
        
        self.settings.write()
        
    def clear(self):
        """
        Clear the settings object so that all sections/keywords are gone
        This function does not write-to-file.  Only clears from memory.
        
        """
        self.settings = configobj.ConfigObj(indent_type="    ")
        self.settings.filename = MAIN_SETTINGS_FILE

    def use_default_settings(self):
        """
        Specify a set of default settings and write to file.
        Called when there is no settings.conf present.
        
        """
        
        self.settings = configobj.ConfigObj(
            DEFAULT_SETTINGS,
            indent_type="    "
        )
        self.settings.filename = MAIN_SETTINGS_FILE
        self.write()
    
    def get_default(self, section, keyword):
        """
        Get the default settings for a section and/or keyword
        If no arguments are given, it just returns all settings
        
        @type section:  string
        @param section: a settings section
        
        @type keyword:  string
        @param keyword: a particular setting in a section
        
        @rtype dict or string
        @return either a dict or string with setting(s)
        
        """
        
        if section is None:
            return DEFAULT_SETTINGS
            
        if keyword is None:
            return DEFAULT_SETTINGS[section]
        
        returner = None
        try:
            returner = DEFAULT_SETTINGS[section][keyword]
        except KeyError:
            print "Error: section %s:%s doesn't exist" % (section, keyword)
            
        return returner

if __name__ == "__main__":
    pass
