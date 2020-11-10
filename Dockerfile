# для deploy
FROM python:3.8

WORKDIR /divorce_project

ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .




# первый рабочий вариант Dockerfile
#FROM python:3.8
#
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        postgresql-client \
#    && rm -rf /var/lib/apt/lists/*
#
#RUN mkdir -p /usr/src/divorce_project/
#WORKDIR /usr/src/divorce_project/
#COPY ./requirements.txt /usr/src/requirements.txt
#RUN pip install -r /usr/src/requirements.txt
#
#COPY . /usr/src/divorce_project/
#
#EXPOSE 8000