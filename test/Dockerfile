FROM python:3.5-alpine

MAINTAINER vensder <vensder@gmail.com>

RUN apk add --update \
    python \
    py-pip \
  && pip install requests \
  && rm -rf /var/chache/apk/*

# base64  Dockerfile  download  pictures  run_tests.py
RUN mkdir /base64 /download
COPY ./pictures /pictures
COPY run_tests.py /run_tests.py
CMD ["python", "run_tests.py"]

