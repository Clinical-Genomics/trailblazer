FROM python:3.11-slim-bullseye

ENV SECRET_KEY="Authkey"
ENV SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"
ENV ANALYSIS_HOST="a_host"
ENV GOOGLE_CLIENT_ID="a_client_id"
ENV GOOGLE_CLIENT_SECRET="a_client_secret"
ENV GOOGLE_REDIRECT_URI="http://localhost:8000/auth"

WORKDIR /home/src/app
COPY . /home/src/app

# Install app requirements
RUN pip install poetry \
&& poetry install


CMD poetry run gunicorn \
  --config gunicorn.conf.py \
  trailblazer.server.app:app

