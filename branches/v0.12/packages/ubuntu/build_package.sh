#!/usr/bin/env bash

# FIXME: this is obviously just an example of the procedure, still need to actually
# write it properly (get the version number from somewhere).

svn export . /tmp/nautilussvn-0.12
cd /tmp
tar -zcvf nautilussvn_0.12.orig.tar.gz nautilussvn-0.12
cd nautilussvn-0.12/
cd packages/ubuntu/
debchange -i
cd ../../
cp -R packages/ubuntu/debian/ .
debuild
