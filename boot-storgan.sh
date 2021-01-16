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
BOOT_FLAG=1
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
    echo "    -k   kill only"
    echo "    -d   debug flag"
    echo "    -h   show this usage"
    echo
}

get_pid() {
    echo `ps x | grep python | sed -n '/storgan/s/ *//p' | cut -d ' ' -f 1`
}

#
# main
#
while getopts hkd OPT; do
    case $OPT in
        k) BOOT_FLAG=0;;
        d) DEBUG_FLAG="-d";;
        h) usage; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

#
# kill
#
PIDS=`get_pid`
while [ ! -z "$PIDS" ]; do
    echo_do "kill $PIDS"
    sleep 1
    PIDS=`get_pid`
done
sleep 2

if [ $BOOT_FLAG -eq 0 ]; then
    exit 0
fi

#
# boot
#
echo_do "$CMD $SUBCMD $DEBUG_FLAG -p $PORT >> $LOGFILE 2>&1 &"
