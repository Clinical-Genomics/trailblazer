FROM docker.io/library/python:3.8-slim@sha256:7bebae21c28738810809ac96734e7a423e6e1e20ebeb6a419e4ddc3f2827ab7b

ENV GUNICORN_WORKERS=1
ENV GUNICORN_TREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400

ENV SECRET_KEY="Authkey"
ENV SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"

WORKDIR /home/src/app
COPY . /home/src/app

RUN pip install -r requirements.txt
RUN pip install -e .


CMD gunicorn \
  --workers=$GUNICORN_WORKERS \
  --bind=$GUNICORN_BIND \
  --threads=$GUNICORN_TREADS \
  --timeout=$GUNICORN_TIMEOUT \
  --proxy-protocol \
  --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
  --log-syslog \
  --access-logfile - \
  --log-level="debug" \
  trailblazer.server.app:app

