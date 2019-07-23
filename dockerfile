# docker pull python:3.7.3
# docker build -t python:3.7.3 -f dockerfile .
FROM python:3.7.3
WORKDIR /
MAINTAINER lsd200
RUN mkdir -p midsc
COPY ./ /midsc/
RUN pip install --upgrade pip && pip install -r midsc/requirements.txt
