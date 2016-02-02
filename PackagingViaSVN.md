**WARNING!** - This page is a work in progress, but is mostly correct except where indicated.

# Introduction #

While it is possible to run NautilusSVN from our tarball releases or even the SVN trunk, most users will probably want to install a package that conforms to the requirements of their particular GNU/Linux distribution.

This page details the methods we use to maintain the packages. There are specific tools for Debian and Ubuntu that make it easy (or at least safe) to perform a lot of common tasks, and these are also given an overview.

_Note: there are also similar tools for Fedora, but I haven't researched them yet._

The examples below are Debian-centric, because that's what I (Jason H) use. Just replaced the **first** occurrence (not all) of `debian` with your distribution:
  * Packaging for Ubuntu (currently Jaunty) is in `/svn/packaging/ubuntu/trunk`
  * Packaging for Debian (always Sid) is in `/svn/packaging/debian/trunk`
  * Packaging for Fedora may be coming soon

# In Short #

## Tagged Release From Tarball ##

To build a particular Debian package (eg. 0.12.1.beta2-3):

  1. Check out **/packages/debian/tags/0.12.1.beta2-3** to (eg) **nautilussvn**
  1. Check out **/packages/debian/tarballs/** to (literally) **tarballs**
  1. Change to the directory in step (1) and run `svn-buildpackage -us -uc`

`svn-buildpackage` is in the Debian package of the same name.

## Build Straight From SVN ##

To build a deb of the trunk for Debian Squeeze:

  * Check out **/trunk** (or just be using your working copy)
  * Merge with **/packaging/debian/nautilussvn/trunk**
    * (on the command line, this is `svn merge http://...repo.../packaging/debian/trunk`)
    * under svn 1.6, you can just do `svn merge ^/packaging/debian/trunk`
    * you can do this the other way around - check out packaging, merge with trunk
  * I recommend running `dch -i` or `dch --local myname` to bump the version up and make it obvious that it's a local build
  * Run `debuild -I -us -uc`

## Build a Snapshot ##

See the notes for using a [SnapshotInstallation](SnapshotInstallation.md).

## Notes ##

  * **svn-buildpackage** will put things in **../build-area**
  * If you don't want to build from an SVN working copy, export your working copy (`svn export . ../nsvn-export`) and use (eg.) **debuild** from your exported dir.

## Notes for NautilusSVN Developers ##

The trunk of the code and trunk of the packaging should be in sync before taking a snapshot. Don't tag a snapshot of the packaging and then commit changes to that — it should always simply come from the packaging trunk.

# Tools #

## Debian and Ubuntu ##

[svn-buildpackage](http://www.debianpaket.de/svn-buildpackage/index.html) - allows you to work on packaging using SVN. We use the [merge-with-upstream mode](http://www.debianpaket.de/svn-buildpackage/ch-import.html#s3.2).

[pbuilder](http://www.netfort.gr.jp/~dancer/software/pbuilder-doc/pbuilder-doc.html) - personal package builder. This creates and maintains a chroot jail for building packages targeted at a specific Debian-like distribution. For example, if you run Debian Squeeze you could use pbuilder to build packages for Debian Sid (unstable) and Ubuntu Jaunty, without needing any other changes to your system. Pbuilder 'starts from scratch' before every build, so it is especially useful for checking that you have all the right build dependencies.

[svn-buildpackage + pbuilder](http://workaround.org/debian-subversion-pbuilder) - these can be used together, and with a bit of tweaking can really streamline package development. Use svn-buildpackage to maintain the repository, and make it call pbuilder to actually do the build.

This can be facilitated with the following lines in **~/.bashrc** (or wherever you like). The first does a proper build for a maintainer to sign and release, the second does a "quick and dirty" build, not making a fuss if you haven't committed changes yet.

```
alias svn-bld='svn-buildpackage --svn-builder="pdebuild --buildresult `pwd`/../build-area --auto-debsign"'
alias svn-bld-q='svn-buildpackage --svn-ignore --svn-builder="pdebuild --buildresult `pwd`/../build-area"'
```

# Repository Structure #

The **packaging** directory, found in the root of the repository, contains subdirectories corresponding to the various distributions we can package for. Depending on the tools used to maintain the various packages, there will be varying structures underneath.

In general though, the packaging directories should contain the upstream tarballs and packaging information ONLY (eg, only the debian dir), if at all possible. Official releases should be tagged.