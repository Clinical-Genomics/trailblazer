FROM python:3.7-slim

ENV GUNICORN_WORKERS=2
ENV GUNICORN_BIND="0.0.0.0:5000"
ENV GUNICORN_TIMEOUT=400

WORKDIR /home/src/app
COPY . /home/src/app

RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 5000

RUN useradd worker
RUN chown -R worker:worker /home/src
USER worker

CMD gunicorn --workers=$GUNICORN_WORKERS --bind=$GUNICORN_BIND --timeout=$GUNICORN_TIMEOUT trailblazer.server.app:app

