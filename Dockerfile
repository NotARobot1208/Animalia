FROM python:3.11.0b3-bullseye

RUN DEBIAN_FRONTEND=noninteractive apt-get install libpq-dev python3-dev
RUN pip3 install flask flask-login psycopg passlib

RUN mkdir /app
COPY . /app



