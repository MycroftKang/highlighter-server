release: python manage.py migrate
web: gunicorn app.wsgi --workers 2 --threads 2 --log-file -
