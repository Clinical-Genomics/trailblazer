FROM python:3.7-slim

WORKDIR /home/src/app
COPY . /home/src/app


RUN pip install -r requirements.txt
RUN pip install -e .
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "trailblazer.server.app:app"]
