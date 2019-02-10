#!/bin/bash
# -*- coding: utf-8 -*-

set -eu

# set up openfst
mkdir -p tmp
cd tmp
wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.9.tar.gz
tar xvfz openfst-1.6.9.tar.gz
cd openfst-1.6.9
patch -p1 < ../../openfst-1.6.9.patch # for Python 3 support
export CFLAGS="-O2"
export CXXFLAGS="-O2"
./configure --prefix=`readlink -m ../../local` --enable-python
make LDFLAGS=-no-undefined install
cd ../..
