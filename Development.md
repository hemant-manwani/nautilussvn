# Introduction #
NautilusSvn is pretty much like any other typical Python program, except it's a Nautilus extension. This has been known in the past to cause some problems, for example with threading.

# Finding your way around the wiki #
There are a couple of pages in the wiki relevant for developers:

  * [CodingStyle](http://code.google.com/p/nautilussvn/wiki/CodingStyle) serves as an introduction to the style we use for our code (also see [PEP 8](http://www.python.org/dev/peps/pep-0008/)).
  * See [Unicode](http://code.google.com/p/nautilussvn/wiki/Unicode) for information on how to properly handle Unicode.
  * [Packaging](http://code.google.com/p/nautilussvn/wiki/Packaging) describes how NautilusSvn should be packages for a number of distros.
  * [Architecture](http://code.google.com/p/nautilussvn/wiki/Architecture) is used for discussion and decisions related mostly to the architecture of NautilusSvn. Also see pages labeled [Phase-Implementation](http://code.google.com/p/nautilussvn/w/list?q=label:Phase-Implementation) and [Phase-Design](http://code.google.com/p/nautilussvn/w/list?q=label:Phase-Design).

# Tips #

## Organizing your code ##

> _See DevelopmentInstallation_

## Starting Nautilus ##
When modifying NautilusSvn you'll have to restart Nautilus quite often. So when you're working on NautilusSvn quit Nautilus first (nautilus -q) and then start it up with:

You can start Nautilus using this alias by:
```
$ nautilus --no-desktop <directory to start in>
```

Whenever you want to reload any changes, simply close the window and start it back up again once you're done.

# Patches #

Patches can either be attached to a [relevant issue](http://code.google.com/p/nautilussvn/issues/list) or submitted to [the mailing list](http://groups.google.com/group/nautilussvn).