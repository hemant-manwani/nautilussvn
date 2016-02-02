

These are the installation instructions for the stable release of NautilusSvn.

# Requirements #
This software requires the following packages to be installed:

  * python-nautilus
  * python-wxgtk2.6
  * python-svn
  * meld (Optional - see [Configuration](http://code.google.com/p/nautilussvn/wiki/Configuration).)

## Ubuntu ##
```
sudo apt-get install python-nautilus python-wxgtk2.6 python-svn meld
```

You still need to follow the manual installation instructions below.

## Fedora ##
Might require some manual work, see [this reply](http://groups.google.com/group/nautilussvn/msg/d63f7323ebba5bb2) in the discussion ["Getting this to work on Fedora 8?"](http://groups.google.com/group/nautilussvn/browse_thread/thread/ce30cd54e11c259/17c3d773b4f9416b)

You still need to follow the manual installation instructions below.

# Installation #
Note that as we update NautiluSvn you'll most likely have to delete everything and start over again as per the most current version of this page. We apologize for the inconvenience, but that's just how development goes. We hope to stabilize the project somewhere after the next release.

## Manual installation ##

```
#!/usr/bin/env bash

# Nautilus extensions live in ~/.nautilus/python-extensions - make sure that this directory exists.
mkdir -p ~/.nautilus/python-extensions/

# Next checkout NautilusSvn into ~/.nautilus/python-extensions/NautilusSvn
cd ~/.nautilus/python-extensions/
svn checkout http://nautilussvn.googlecode.com/svn/branches/stable NautilusSvn

# Setup the emblems
mkdir -p ~/.icons/hicolor/scalable
ln -s ~/.nautilus/python-extensions/NautilusSvn/icons ~/.icons/hicolor/scalable/emblems # The current emblems folder
ln -s ~/.nautilus/python-extensions/NautilusSvn/icons ~/.icons/hicolor/scalable/icons # The old emblems folder

# Finally we need to set up a symlink so that Nautilus finds the correct startup script. 
ln -s NautilusSvn/NautilusSvn.py NautilusSvn.py

# Now just restart Nautilus, and you should see the new Subversion menu items.
# 1) nautilus -q && nautilus
# 2) killall nautilus
# 3) log out and back in again

nautilus -q && nautilus
```