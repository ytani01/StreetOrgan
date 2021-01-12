#!/bin/sh -e
#
# Street Organ Roll Book Maker
#
#   (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`
cd_echo $MYDIR
MYDIR=`pwd`
BINDIR="$HOME/bin"

MY_PKG="storgan"

WRAPPER_SCRIPT="StOrgan"
BOOT_SCRIPT="boot-storgn.sh"
BIN_FILES="$WRAPPER_SCRIPT $BOOT_SCRIPT"

PKGS_TXT="pkgs.txt"
ENV_FILE="storgan-env"
CONF="storgan.conf"

GITHUB_TOP="https://github.com/ytani01"

MIDILIB_PKG="midilib"
MIDILIB_DIR="MIDI-lib"
MIDILIB_GIT="${GITHUB_TOP}/${MIDILIB_DIR}.git"

CUILIB_PKG="cuilib"
CUILIB_DIR="CuiLib"
CUILIB_GIT="${GITHUB_TOP}/${CUILIB_DIR}.git"

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

install_my_python_pkg() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### install/update $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo $_DIR
    git pull
    pip install .
    echo
}

#
# main
#

#
# install Linux packages
#
if [ -f $PKGS_TXT ]; then
    echo "### install Linux packages"
    echo
    sudo apt install `cat $PKGS_TXT`
    echo
fi

#
# venv
#
if [ -z $VIRTUAL_ENV ]; then
    if [ ! -f ../bin/activate ]; then
        echo
        echo "ERROR: Please create and activate Python3 Virtualenv(venv) and run again"
        echo
        echo "\$ cd ~"
        echo "\$ python -m venv env1"
        echo "\$ . ~/env1/bin/activate"
        echo
        exit 1
    fi
    echo "### activate venv"
    . ../bin/activate
fi
cd_echo $VIRTUAL_ENV

echo "### create $HOME/$ENV_FILE"
echo "STORGAN_DIR=$MYDIR" > $HOME/$ENV_FILE
echo "VENVDIR=$VIRTUAL_ENV" >> $HOME/$ENV_FILE
echo
cat $HOME/$ENV_FILE
echo

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
echo
pip install -U pip setuptools wheel
hash -r
echo
pip -V
echo

#
# install my python packages
#
install_my_python_pkg $MIDILIB_PKG $MIDILIB_DIR $MIDILIB_GIT
install_my_python_pkg $CUILIB_PKG $CUILIB_DIR $CUILIB_GIT

#
# install my package
#
cd_echo $MYDIR
echo "### install main python package"
echo
pip install .
echo

#
# install scripts
#
echo "### install scripts"
echo
if [ ! -d $BINDIR ]; then
    mkdir -pv $BINDIR
fi
cp -fv $BIN_FILES $BINDIR
echo

echo "### usage"
echo
$WRAPPER_SCRIPT --help
echo
