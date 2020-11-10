#!/bin/sh

if [ "$DATABASE" = "divorceDB" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      echo "I'm here"
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#команда для полной очистки очистки БД
#python manage.py flush --no-input
python manage.py migrate

exec "$@"