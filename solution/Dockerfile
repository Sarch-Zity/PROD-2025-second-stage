FROM python:3.12.1-alpine3.19

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
WORKDIR /usr/src/app/application

ENV SERVER_PORT=8080

CMD ["sh", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:${SERVER_PORT}"]
