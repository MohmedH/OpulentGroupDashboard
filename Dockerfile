FROM python:3.6

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py requirements-pgsql.txt config.py .env ./
COPY app app
COPY migrations migrations
COPY database.db database.db

RUN pip install -r requirements-pgsql.txt

EXPOSE 5005



CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]