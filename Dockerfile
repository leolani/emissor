# syntax = docker/dockerfile:1.2

FROM python:3.7.10

WORKDIR emissorui

COPY requirements.ui.txt setup.py VERSION ./
COPY app.py ./
COPY emissor ./emissor
COPY webapp/dist/emissor-annotation ./webapp/dist/emissor-annotation

RUN pip install --upgrade pip && pip install -r requirements.ui.txt

ENV EMISSOR_PORT=5000

CMD python app.py --port "$EMISSOR_PORT"
