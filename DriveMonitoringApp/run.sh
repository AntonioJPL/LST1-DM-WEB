#!/bin/bash

# wait for wal mysql database
#while [ "$(echo 'show databases;' | mysql -h mysql -u $MYSQL_USER -p$MYSQL_PASSWORD | grep $MYSQL_DATABASE | wc -l)" -eq "0" ]
#do
#    echo "Waiting for mysql $MYSQL_DATABASE database..."
#    sleep 10
#done

# start python server
python3 manage.py runserver 0.0.0.0:8000