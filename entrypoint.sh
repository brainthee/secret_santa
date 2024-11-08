#!/bin/sh

cd /app 

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

sudo -Eu user -- python3 manage.py migrate --noinput
# sudo -Eu user -- /usr/bin/crontab /crontab.txt

exec "$@"