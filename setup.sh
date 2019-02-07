#!/bin/bash
# -*- coding: utf-8 -*-

set -eu

# set up openfst
mkdir -p tmp
cd tmp
wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.3.4.tar.gz
tar xvfz openfst-1.3.4.tar.gz
cd openfst-1.3.4
./configure --prefix=`readlink -m ../../local`
make install
cd ../..

# set up pyfst
pip install pyfst --global-option=build_ext --global-option="-I`pwd`/local/include" --global-option="-L`pwd`/local/lib" --install-option="--prefix=`pwd`/local" --ignore-installed
