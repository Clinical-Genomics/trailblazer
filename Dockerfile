FROM python:3.7-slim

WORKDIR /home/src/app
COPY . /home/src/app

RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 5000

RUN useradd worker
USER worker

