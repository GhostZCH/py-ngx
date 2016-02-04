#!/usr/bin/env bash


if [ "$1" == "reload" ]; then
    pid=`cat py-ngx.pid`
    echo pid = ${pid} reloading...
    kill -10 ${pid}
elif [ "$1" == "close" ]; then
    pid=`cat py-ngx.pid`
    echo pid = ${pid} close...
    kill -15 ${pid}
else
    python pyngx.py
fi
