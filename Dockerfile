# syntax=docker/dockerfile:1

FROM python:3

WORKDIR /reqs

COPY Pipfile.lock Pipfile.lock

RUN pipenv install