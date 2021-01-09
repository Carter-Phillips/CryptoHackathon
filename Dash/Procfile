web: gunicorn app:server --log
worker-default: celery -A tasks worker --loglevel=info
worker-beat: celery -A tasks beat --loglevel=info
