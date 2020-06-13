FROM python:3-alpine

WORKDIR /usr/app

RUN apk update
RUN apk add postgresql-dev g++ python3-dev

COPY ./requirements.txt .
RUN pip install -U pip
RUN pip install -Ur requirements.txt

COPY . .
