#!/bin/bash

set -e

help() {
    echo "Usage: docker run -dti --link mysql:mysql -e AD_SERVER=value1 -e USER_SVC=value2 -e PASS_SVC=value3  -e MYSQL_HOST=value5 -e MYSQL_USER=value6 -e MYSQL_PASS=value7 -e MYSQL_DB=value8 image:tag" >&2
    echo
    echo "   AD_SERVER           hostname active directory"
    echo "   USER_SVC            service user for connecting the active directory"
    echo "   PASS_SVC            passowrd of service user for connecting the active directory"
    echo "   MYSQL_HOST          hostname mysql database"
    echo "   MYSQL_USER          user for connecting the mysql database"
    echo "   MYSQL_PASS          passowrd of user for connecting the database"
    echo "   MYSQL_DB            name database for connect "
    echo
    exit 1
}

if [ ! -z "$AD_SERVER" ] || [ ! -z "$USER_SVC" ] || [ ! -z "$PASS_SVC" ]|| [ ! -z "$API_DB" ] || [ ! -z "$MYSQL_HOST" ] || [ ! -z "$MYSQL_USER" ] || [ ! -z "$MYSQL_PASS" ]|| [ ! -z "$MYSQL_DB" ]; then

	sed -i "s/adserver/$AD_SERVER/g" /opt/app.py
	sed -i "s/passsvc/$PASS_SVC/g" /opt/app.py
	sed -i "s/apidb/$API_DB/g" /opt/app.py
	sed -i "s/usersvc/$USER_SVC/g" /opt/app.py

	sed -i "s/mysqlhost/$MYSQL_HOST/g" /opt/app.py
	sed -i "s/mysqluser/$MYSQL_USER/g" /opt/app.py
	sed -i "s/mysqlpass/$MYSQL_PASS/g" /opt/app.py
	sed -i "s/dbmysql/$MYSQL_DB/g" /opt/app.py

    /usr/local/bin/python  /opt/app.py & 
    #/usr/sbin/ntpdate a.ntp.br &
    /etc/init.d/rabbitmq-server start 
    /usr/sbin/rabbitmqctl add_vhost myvhost
    /usr/sbin/rabbitmqctl set_permissions -p myvhost guest ".*" ".*" ".*"    

else
	echo "Please enter the required data!"
	help

fi

exec "$@"
