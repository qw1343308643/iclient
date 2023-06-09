#!/bin/bash
#参数一  安装目录
#参数二  主机名
#参数三  服务器ip
if [ $# -lt 3 ]; then
   echo "Usage:`basename $0` DesDir HostName ServerIp"
   exit 1
fi
cp -rf . $1

CurrentDir=`pwd`
cd "$1"
DesDir=`pwd`
cd "$CurrentDir"

CommandTime="*/1 * * * * "
CommandPath="$DesDir/CheckProcess.sh $2 $3 >>/dev/null"
Command="${CommandTime}""${CommandPath}"
python3 ./StartUp.py --cmd="$CommandPath"
crontab -l &> /dev/null
if [ $? != 0 ];then
   echo "$Command" >> tmpCron && crontab tmpCron && rm -f tmpCron
else
   Installed=`crontab -l | grep $2`
   if [ "${Installed}" != "" ];then
       crontab -l > tmpCron && sed -n 's/"$Installed"/"$Command"/' tmpCron && crontab tmpCron && rm -f tmpCron
   else
       crontab -l > tmpCron && echo "$Command" >> tmpCron && crontab tmpCron && rm -f tmpCron

   fi
fi
