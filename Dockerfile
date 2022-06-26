FROM python:3.11.0b3-bullseye

RUN apt-get update 
RUN DEBIAN_FRONTEND=noninteractive apt-get install libpq-dev python3-dev curl -y
RUN pip3 install flask flask-login psycopg2 passlib requests websockets

RUN mkdir /app
RUN mkdir /root/.postgresql
COPY . /app

EXPOSE 8080
EXPOSE 8081

CMD ["/bin/sh", "-c", "bash /app/run.sh"]


