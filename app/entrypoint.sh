#!/bin/bash

set +e

if [ -f "/usr/src/app/build.env" ]; then
    source "/usr/src/app/build.env"
fi

ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
echo "Europe/Moscow" > /etc/timezone

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

cd /usr/src/app

echo "Executing: python main.py --setup_db"

python main.py --setup_db

echo "Executing: $@"

#sleep 9999h

exec "$@"