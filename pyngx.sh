#!/usr/bin/env bash

pid=`cat py-ngx.pid`

if [ "$1" == "reload" ]; then
    echo pid = ${pid} reloading...
    kill -10 ${pid}
elif [ "$1" == "close" ]; then
    echo pid = ${pid} close...
    kill -15 ${pid}
else
    python pyngx.py
fi
