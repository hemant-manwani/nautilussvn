

# Dependencies #

Here is a basic set of dependencies that you will need to install before you can install NautilusSvn.  The actual package names are different for each distribution.

| **Program** | **Description** |
|:------------|:----------------|
| [nautilus-python](http://svn.gnome.org/viewvc/nautilus-python/) | Nautilus extension python bindings |
| [configobj](http://www.voidspace.org.uk/python/configobj.html) | Python configuration module |
| [pygtk](http://www.pygtk.org/) | GTK+ python bindings |
| [pysvn](http://pysvn.tigris.org/) | Subversion python bindings |
| [subversion](http://subversion.tigris.org/) | Subversion, duh! |
| [meld](http://meld.sourceforge.net/) | A GTK+ diff tool |

# Distro-specific instructions #

## Ubuntu 8.04 and later ##

1. Install the following packages through your package manager.
```
sudo apt-get install python-nautilus python-configobj python-gtk2 python-glade2 python-svn subversion meld
```

2. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)

## Fedora 10 ##

1. Install Packages:
```
yum install nautilus-python pysvn python-configobj python-devel subversion meld
```

Note for x86\_64: As root, run **ln -s /usr/lib64/libpython2.5.so /usr/lib/libpython2.5.so**.  Otherwise you will get various import errors for libpython and libpyglib.

3. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)

## Arch Linux ##

All of the packages required to run nautilussvn can be found in Arch Linux User-community Repository (AUR). You can download and build them from there, or use yaourt to simplify the process.

1. Install packages using yaourt:

```
yaourt -S python-nautilus python-configobj pygtk pysvn subversion meld
```

2. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)

## OpenSUSE 11.1 ##

1. In Yast -> Software Repositories.  Add the GNOME:STABLE and GNOME:Community repositories.

2. Install packages:
```
zypper install python-nautilus python-gtk python-gtk-devel python-pysvn subversion meld
```

3. Get python-configobj at http://www.voidspace.org.uk/python/configobj.html#files
  * Copy configobj.py to /usr/lib/python2.6/site-packages/

4. Edit the file /usr/lib/python2.6/site-packages/pysvn/init.py
> There is a place where it says:
```
elif maj_min == (2,5):
    ....  
```
> Add another elif block, like this...
```
elif maj_min == (2,6):
    import _pysvn_2_6
    _pysvn = _pysvn_2_6
```

5. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)

## Mandriva 2009.0 and 2009.1 ##

1.
```
urpmi nautilus-python python-pysvn python-configobj subversion meld 
```

2. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)

## CentOS 5.2 ##

Note: Even with no dbus requirement, still doesn't work well.  The nautilus-python (0.5.0) doesn't work very well.

1. Add the RPMForge Repositories.  Instructions are at http://wiki.centos.org/AdditionalResources/Repositories/RPMForge

2. Install Packages:
```
yum install pygtk2 subversion subversion-devel gcc gcc-c++ neon-devel python-devel pygtk2-devel eel2 eel2-devel python-configobj nautilus-devel meld
```

3. Download nautilus-python bindings at http://ftp.acc.umu.se/pub/GNOME/sources/nautilus-python
  * Make sure you get v0.5.0, NOT v0.5.1
  * Build/install with: su -c './configure ; make ; make install'

5. Download and build the pysvn extension source kit.  You'll need one built to work for subversion 1.4.
  * http://pysvn.tigris.org/project_downloads.html
  * Uncompress the pysvn tar.gz file then run the following commands:
```
cd Source
python setup.py backport
python setup.py configure
make
mkdir /usr/lib/python2.4/site-packages/pysvn
cp pysvn/__init__.py /usr/lib/python2.4/site-packages/pysvn
cp pysvn/_pysvn_2_4.so /usr/lib/python2.4/site-packages/pysvn
```

6. [Install the Extension](http://code.google.com/p/nautilussvn/wiki/ManualInstallation)