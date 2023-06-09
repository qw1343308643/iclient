#!/bin/bash
#参数一  主机名
#参数二  服务器ip
#判断进程是否存在，如果不存在就启动它
cd `dirname $0`
PIDS=`ps -ef |grep "\./NetTestPyClient" |grep -v grep | awk '{print $2}'`
if [ "$PIDS" == "" ]; then
HOSTNAME=`hostname`
	if [ "$HOSTNAME" != $1 ]; then
		hostname $1
	fi
python ./NetTestPyClient.py -ip $2
fi
