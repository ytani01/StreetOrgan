#!/bin/sh -e
#
# Street Organ Roll Book Maker
#
#   (c) 2021 Yoichi Tanibayashi
#
############################################################
help() {
    cat <<'END'

[インストール後のディレクトリ構造]

 $HOME/ .. ホームディレクトリ
    |
    +- bin/ .. $BINDIR  シェルスクリプトなど
    |   |
    |   +- Storgan .. $WRAPPER_SCRIPT  wrapper script
    |   +- boot-storgan.sh .. $BOOT_SCRIPT  起動スクリプト
    |
    +- storgan/ .. $WORKDIR
    |   |
    |   +- storgan.conf .. $CONF_FILE  設定ファイル
    |   |
    |   +- webroot/ .. $WEBROOT
    |   |   |
    |   |   +- template/
    |   |   +- static/
    |   |       |
    |   |       +- js/
    |   |       +- css/
    |   |       |
    |   |       +- midi/
    |   |       +- svg/
    |   |
    |   +- log/ .. $LOGDIR
    |
    +- env1/  ... python3 Virtualenv(venv) 【ユーザが作成する】
        |
        +- StreetOrgan/ ... ``StreetOrgan`` gitリポジトリ
        |
        | 【以下、インストールに必要なライブラリなど】
        |
        +- MIDI-lib/
        :

END
}

############################################################
MYNAME=`basename $0`
MYDIR=`dirname $0`
BINDIR="$HOME/bin"


WRAPPER_SCRIPT="Storgan"
echo "WRAPPER_SCRIPT=$WRAPPER_SCRIPT"


BUILD_DIR="$MYDIR/build"

WRAPPER_SRC="$WRAPPER_SCRIPT.in"
echo "WRAPPER_SRC=$WRAPPER_SRC"

MY_PYTHON_PKG=`echo $WRAPPER_SCRIPT | tr "A-Z" "a-z"`
echo "MY_PYTHON_PKG=$MY_PYTHON_PKG"

BOOT_SCRIPT="boot-$MY_PYTHON_PKG.sh"
echo "BOOT_SCRIPT=$BOOT_SCRIPT"

CONF_FILE="$MY_PYTHON_PKG.conf"
echo "CONF_FILE=$CONF_FILE"

WORKDIR="$HOME/storgan"
echo "WORKDIR=$WORKDIR"

WEBROOT="webroot"
echo "WEBROOT=$WEBROOT"

LOGDIR="$WORKDIR/log"
echo "LOGDIR=$LOGDIR"

PKGS_TXT="pkgs.txt"

GITHUB_TOP="https://github.com/ytani01"

MIDILIB_PKG="midilib"
MIDILIB_DIR="MIDI-lib"
MIDILIB_GIT="${GITHUB_TOP}/${MIDILIB_DIR}.git"
echo "$MIDILIB_PKG $MIDILIB_DIR $MIDILIB_GIT"

INSTALLED_FILE="$MYDIR/build/installed"
mkdir -pv $MYDIR/build

FAST_MODE=

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

install_external_python_pkg() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### install/update $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo ./$_DIR
    git pull
    pip install .
    echo
}

usage() {
    echo
    echo "  Usage: $MYNAME [-u] [-h]"
    echo
    echo "    -f  fast mode"
    echo "    -u  uninstall"
    echo "    -h  show this usage"
    echo
}

uninstall() {
    cd_echo $MYDIR
    
    echo "### remove installed files"
    echo
    rm -fv `cat $INSTALLED_FILE`
    echo

    echo "### uninstall python packages"
    echo
    pip uninstall -y $MY_PYTHON_PKG
    echo

    echo "### remove build/"
    echo
    #rm -rfv $MYDIR/build
}

#
# main
#
cd_echo $MYDIR
MYDIR=`pwd`

while getopts fuh OPT; do
    case $OPT in
        f) FAST_MODE=1;;
        u) uninstall; exit 0;;
        h) usage; help; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

echo -n > $INSTALLED_FILE

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

#
# build wrapper script
#
cd_echo $MYDIR
mkdir -pv $BUILD_DIR

echo "### build $WRAPPER_SCRIPT"
sed -e "s?%%% MY_PYTHON_PKG %%%?$MY_PYTHON_PKG?" \
    -e "s?%%% MY_GITDIR %%%?$MYDIR?" \
    -e "s?%%% CONF_FILE %%%?$CONF_FILE?" \
    -e "s?%%% VENVDIR %%%?$VIRTUAL_ENV?" \
    -e "s?%%% WORKDIR %%%?$WORKDIR?" \
    -e "s?%%% WEBROOT %%%?$WEBROOT?" \
    $WRAPPER_SRC > $BUILD_DIR/$WRAPPER_SCRIPT
chmod +x $BUILD_DIR/$WRAPPER_SCRIPT

echo '-----'
cat $BUILD_DIR/$WRAPPER_SCRIPT | sed -n -e '1,/\#* main/p'
echo '  :'
echo '-----'
echo

echo $BUILD_DIR/$WRAPPER_SCRIPT >> $INSTALLED_FILE

#
# install scripts and conf_file
#
echo "### install scripts"
echo
if [ ! -d $BINDIR ]; then
    mkdir -pv $BINDIR
fi
for f in $BUILD_DIR/$WRAPPER_SCRIPT $BOOT_SCRIPT; do
    if [ -f $f ]; then
        cp -fv $f $BINDIR
        echo $BINDIR/`basename $f` >> $INSTALLED_FILE
    fi
done
cp -fv $CONF_FILE-sample $BINDIR/$CONF_FILE
echo $BINDIR/$CONF_FILE >> $INSTALLED_FILE
echo

#
# install work dir
#
cd_echo $MYDIR
echo "### work directory"
echo
mkdir -pv $WORKDIR $LOGDIR
cp -rfv $WEBROOT $WORKDIR
echo

#
# update pip, setuptools, and wheel
#
if [ -z $FAST_MODE ]; then
    echo "### insall/update pip etc. .."
    echo
    pip install -U pip setuptools wheel
    hash -r
    echo
    pip -V
    echo
fi

#
# install my python packages
#
if [ -z $FAST_MODE ]; then
    install_external_python_pkg $MIDILIB_PKG $MIDILIB_DIR $MIDILIB_GIT
fi

#
# install my package
#
cd_echo $MYDIR
echo "### install main python package"
echo
pip install .
echo

echo "### usage"
echo
$WRAPPER_SCRIPT --help
echo
