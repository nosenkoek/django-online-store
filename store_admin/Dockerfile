FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /store_app
COPY requirements.txt /store_app/

RUN pip install -r requirements.txt

COPY . /store_app