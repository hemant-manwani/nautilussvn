#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2008 by Adam Plumb <adamplumb@gmail.com>
# 
# NautilusSvn is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# NautilusSvn is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NautilusSvn;  If not, see <http://www.gnu.org/licenses/>.
#

"""
Provides a simple wrapper around the python logger.

Right now there is the base Log class, and three specialized classes that 
inherit from the Log class: ConsoleLog, FileLog, and DualLog.  ConsoleLog logs
messages to the standard output (command line), FileLog outputs to a log file,
and DualLog outputs to both.

The programmer does not need to think about the logger types because this will
be specified in the user's settings.  So to set up your module to log do the 
following:

Usage:
    from nautilussvn.lib.log import Log

    log = Log("my.module")
    log.debug("a debug message")

"""

from os.path import expanduser
import logging
import logging.handlers

from nautilussvn.lib.settings import SettingsManager

LEVELS = {
    "debug":    logging.DEBUG,
    "info":     logging.INFO,
    "warning":  logging.WARNING,
    "error":    logging.ERROR,
    "critical": logging.CRITICAL
}

sm = SettingsManager()
DEFAULT_LEVEL = sm.get("logging", "level").lower()
DEFAULT_LOG_TYPE = sm.get("logging", "type")

changed = False
if DEFAULT_LEVEL not in LEVELS:
    DEFAULT_LEVEL = "debug"
    sm.set("logging", "level", DEFAULT_LEVEL.title())
    changed = True
    
if not DEFAULT_LOG_TYPE:
    DEFAULT_LOG_TYPE = "Console"
    sm.set("logging", "type", DEFAULT_LOG_TYPE)
    changed = True

if changed:
    sm.write()

LOG_PATH = expanduser("~/.nautilussvn/NautilusSvn.log")
DEFAULT_FORMAT = "%(message)s"
FILE_FORMAT = "%(asctime)s %(levelname)s\t%(name)s\t\t%(message)s"
CONSOLE_FORMAT = "%(levelname)s\t%(name)s\t\t%(message)s"

class BaseLog:
    """
    Provides a wrapper around the logging module to simplify some logging tasks.
    This base class should generally not be called.
    
    """
    
    def __init__(self, logger="", level=DEFAULT_LEVEL):
        self.logger = logging.getLogger(logger)
        self.level = level
        self.logger.setLevel(LEVELS[level])
        self.handler = None
    
    def set_level(self, level=DEFAULT_LEVEL):
        """
        Set the mimimum level to be logged.
        
        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical)
        
        """
        
        self.level = level
        self.logger.setLevel(LEVELS[level])
    
    def debug(self, msg=""):
        """
        Pass a debug level log message (Numeric value: 10)
        
        @type   msg: string
        @param  msg: The message to pass
        
        """
        
        self.logger.debug(msg)
    
    def info(self, msg=""):
        """
        Pass an info level log message (Numeric value: 20)
        
        @type   msg: string
        @param  msg: The message to pass
        
        """
        
        self.logger.info(msg)
    
    def warning(self, msg=""):
        """
        Pass a warning level log message (Numeric value: 30)
        
        @type   msg: string
        @param  msg: The message to pass
        
        """
        
        self.logger.warning(msg)
        
    def error(self, msg=""):
        """
        Pass an error level log message (Numeric value: 40)
        
        @type   msg: string
        @param  msg: The message to pass
        
        """
        
        self.logger.error(msg)
    
    def critical(self, msg=""):
        """
        Pass a critical level log message (Numeric value: 50)
        
        @type   msg: string
        @param  msg: The message to pass
        
        """
        
        self.logger.critical(msg)
    
    def set_handler(self, handler, format=DEFAULT_FORMAT):
        """
        Set how the logging module should handle log messages.
        
        @type   handler: logging.Handler
        @param  handler: The class that handles log messages
        
        @type   format: string
        @param  format: The formatting to be used when displaying messages
        
        """
        
        self.handler = handler
        self.handler.setLevel(LEVELS[self.level])
        self.handler.setFormatter(logging.Formatter(format))
        self.logger.addHandler(self.handler)

class ConsoleLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to the
    command line/standard output.
    
    Usage:
        clog = ConsoleLog("nautilussvn.ui.commit")
        clog.debug("This function needs refactoring")
        clog.error("You just screwed the pooch!")
    
    """
    
    def __init__(self, logger="", level=DEFAULT_LEVEL):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages
        
        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical) 
        
        """
        
        BaseLog.__init__(self, logger, level)
        self.set_handler(logging.StreamHandler(), CONSOLE_FORMAT)

class FileLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to file
    which is automatically rotated every day and keeps seven days worth of data.
    
    Usage:
        flog = FileLog("nautilussvn.ui.commit")
        flog.debug("This function needs refactoring")
        flog.error("You just screwed the pooch!")
    
    """

    def __init__(self, logger="", level=DEFAULT_LEVEL):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages
        
        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical) 
        
        """

        BaseLog.__init__(self, logger, level)
        self.set_handler(
            logging.handlers.TimedRotatingFileHandler(LOG_PATH, "D", 1, 7, "utf-8"), 
            FILE_FORMAT
        )

class DualLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to both the
    command line/standard output and a file which is automatically rotated every
    day.
    
    Usage:
        dlog = DualLog("nautilussvn.ui.commit")
        dlog.debug("This function needs refactoring")
        dlog.error("You just screwed the pooch!")
    
    """

    def __init__(self, logger="", level=DEFAULT_LEVEL):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages
        
        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical) 
        
        """
        
        BaseLog.__init__(self, logger, level)
        self.set_handler(
            logging.handlers.TimedRotatingFileHandler(LOG_PATH, "D", 1, 7, "utf-8"), 
            FILE_FORMAT
        )
        self.set_handler(logging.StreamHandler(), CONSOLE_FORMAT)

class NullHandler(logging.Handler):
    """
    Handles log messages and doesn't do anything with them
    
    """

    def emit(self, record):
        pass

class NullLog(BaseLog):
    """
    If the user does not want to generate a log file, use the NullLog.  It calls
    the NullHandler class as its handler.    
    
    """

    def __init__(self, *args, **kwargs):
        BaseLog.__init__(self, *args, **kwargs)
        self.set_handler(NullHandler())

Log = NullLog
if DEFAULT_LOG_TYPE == "File":
    Log = FileLog
elif DEFAULT_LOG_TYPE == "Console":
    Log = ConsoleLog
elif DEFAULT_LOG_TYPE == "Both":
    Log = DualLog
