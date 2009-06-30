from __future__ import absolute_import 

import os

import gettext as _gettext
import locale
from locale import getdefaultlocale

from nautilussvn import APP_NAME

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S" # for log files
LOCAL_DATETIME_FORMAT = locale.nl_langinfo(locale.D_T_FMT) # for UIs

LOCALE_DIR = "%s/locale" % os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = "/usr/share/locale"

langs = []
language = os.environ.get('LANGUAGE', None)
if language:
    langs += language.split(":")
langs += [getdefaultlocale()[0]]
if not langs:
    langs = ["en_US"]

_gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
_gettext.textdomain(APP_NAME)

gettext = _gettext.translation(APP_NAME, LOCALE_DIR, languages=langs, fallback=True)

def initialize_locale():
    _locale, encoding = locale.getdefaultlocale()
    if _locale is None:
        _locale = "en_US"
    if encoding is None:
        encoding = "utf8"
        
    locale.setlocale(locale.LC_ALL, (_locale, encoding))
