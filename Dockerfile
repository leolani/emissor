# syntax = docker/dockerfile:1.2

FROM python:3.7.10

WORKDIR emissorui

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app.py ./
COPY emissor ./emissor
COPY webapp ./webapp

ENV EMISSOR_PORT=5000

CMD python app.py --port "$EMISSOR_PORT"