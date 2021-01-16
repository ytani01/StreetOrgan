#!/bin/sh
#
# boot script
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`


CMD_NAME=Storgan
PORT=10081

SUBCMD="webapp"
CMD=$HOME/bin/$CMD_NAME
LOGDIR=$HOME/storgan/log
LOGFILE=$LOGDIR/$CMD_NAME.log
DEBUG_FLAG=

#
# functions
#
echo_do() {
    _TS=`date +'%F %T'`
    echo "$_TS $*"
    eval "$*"
    return $?
}

usage() {
    echo
    echo "  $CMD_NAME boot script"
    echo
    echo "  Usage: $MYNAME [-h] [-d]"
    echo
    echo "    -d   debug flag"
    echo "    -h   show this usage"
    echo
}

#
# main
#
while getopts hkd OPT; do
    case $OPT in
        h) usage; exit 0;;
        d) DEBUG_FLAG="-d";;
        *) usage; exit 1;;
    esac
    shift
done

#
# boot
#
echo_do "$CMD $SUBCMD $DEBUG_FLAG -p $PORT >> $LOGFILE 2>&1 &"
