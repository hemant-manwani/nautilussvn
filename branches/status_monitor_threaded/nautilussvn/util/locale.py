from __future__ import absolute_import 

import os

import gettext as _gettext
from locale import getdefaultlocale

from nautilussvn import APP_NAME

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
