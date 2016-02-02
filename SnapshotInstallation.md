## Personal Copy ##

We tag development snapshots as we go, so people can try "testing" versions of NautilusSVN. If you don't want to install things system-wide (wise for a single user system), check out the [development installation](DevelopmentInstallation.md) instructions, and remember to substitute **trunk** with **tags/latest-snapshot**.

**Please note** that even though these are testing snapshots, they're still not releases. In fact, they're emphatically NOT release ready. If you have problems, we'd really appreciate the feedback.

## System-Wide Install: No Packaging ##

You can pull the development snapshot from our repository and install the extension globally using the setup script (setup.py), here's how:

```
mkdir ~/Development
svn checkout http://nautilussvn.googlecode.com/svn/tags/latest-snapshot ~/Development/nautilussvn
cd ~/Development/nautilussvn
sudo python setup.py install
nautilus -q && nautilus &
```

After that you only have to svn update to get the latest snapshot.

## System-Wide Install: Packaged ##

If you want to build a development snapshot, you don't really need to bother about a checkout (since you're packaging the results anyway). Better to do an export, as per below. See also the [packaging from SVN](PackagingViaSvn.md) instructions.

1. Change to your working dir and export the development snapshot :
```
svn --force export http://nautilussvn.googlecode.com/svn/tags/latest-snapshot .
svn --force export http://nautilussvn.googlecode.com/svn/packaging/distribution/tags/snapshot .
```

...replace **distribution** with ubuntu, debian or whatever else.

2. Install build dependencies. For an installed package it's:
```
sudo aptitude build-dep nautilussvn
```

...but I don't think this works for uninstalled packages. If you're using [pbuilder](http://www.netfort.gr.jp/~dancer/software/pbuilder-doc/pbuilder-doc.html), skip this step.

3. Change the version:

```
dch --local snapshot "Snapshot build."
```

3. Build the package:

Personally, I like [pbuilder](http://www.netfort.gr.jp/~dancer/software/pbuilder-doc/pbuilder-doc.html). But these instructions use **debuild**:

```
debuild -us -uc -b
```

4. Install the package. Ubuntu users have a graphical interface for that (I think), and Debian users can tough it out until someone writes one (I use a local repo in /var/repository, STW for instructions or just use `dpkg -i` and sort out dependencies later).