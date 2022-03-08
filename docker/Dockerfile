FROM python:3.8.8-alpine as os

WORKDIR /usr/src/app

FROM os as python-env

RUN apk update && apk add gcc musl-dev

COPY ./app/requirements.txt .
RUN pip install --upgrade pip wheel
RUN pip install -r /usr/src/app/requirements.txt

FROM python-env
ENV DATABASE=postgres
COPY ./app .

ENTRYPOINT [ "sh", "/usr/src/app/entrypoint.sh" ]