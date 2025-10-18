#!/bin/bash
echo "Makemigrations"
python manage.py makemigrations core --noinput
echo "==============================="

echo "Migrate"
python manage.py migrate --noinput
echo "==============================="

echo "Scrape default articles"
python manage.py scrape_articles
echo "==============================="

echo "Start server"
exec python manage.py runserver 0.0.0.0:8000