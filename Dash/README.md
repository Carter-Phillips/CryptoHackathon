# Instructions

Run each command in it's own terminal. You should have three terminals.

## Linux
1. Celery scheduler:
`celery -A tasks beat --loglevel=DEBUG`

2. Celery worker:
`celery -A tasks worker --loglevel=DEBUG`

3. The dash app:
`python3 app.py`

## Windows
1. Celery scheduler:
`celery -A tasks beat --loglevel=DEBUG`

2. Celery worker (ensure you have `gevent` -> `pip install gevent`):
`celery -A tasks worker --loglevel=DEBUG info -P gevent`

3. The dash app:
`python app.py`