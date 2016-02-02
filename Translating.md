# Introduction #

Translating NautilusSvn is a fairly simple process.  We provide a template file that has the English text from our program and a space for the translated text that you will write.  The template file is located at nautilussvn/po/NautilusSvn.pot.

# Dependencies #

You will need the gettext and intltool utilities.

# Start a new translation #

Figure out your language and locale (i.e. en\_US is English/United States, en\_CA is English/Canada).  For a list of locale code, go [here](http://www.loc.gov/standards/iso639-2/php/code_list.php).  And for a list of country codes, go [here](http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm).

Once you open your terminal emulator, type:
```
$ cd /path/to/nautilussvn
$ msginit --input=po/NautilusSvn.pot --locale=en_CA
$ mv en_CA.po po/en_CA.po
```

After updating the po/en\_CA.po file with your translations, type:
```
$ mkdir -p locale/en_CA/LC_MESSAGES
$ msgfmt --output-file=locale/en_CA/LC_MESSAGES/NautilusSvn.mo po/en_CA.po
```

# Translating with a GUI #

Several programs have been created specifically for translating with .po files.  Here is a short list:

  * [Poedit](http://www.poedit.net/)

# Getting your translation to us #

Open a new issue in our [Issue Tracker](http://code.google.com/p/nautilussvn/wiki/Issues?tm=3) and attach the NautilusSvn.mo and .po files that you created.  We will immediately update our development trunk, and it will be included in the next official release.