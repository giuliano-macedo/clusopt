# docker build -t clusopt .
# docker run -it -p 3523:3523 clusopt bash
FROM python:3.7.3
MAINTAINER llpinokio
WORKDIR /
RUN mkdir -p clusopt
COPY ./ /clusopt/
RUN apt update && apt install -y libboost-thread-dev
RUN pip install --upgrade pip && pip install -r clusopt/requirements.txt
WORKDIR /clusopt/src/
EXPOSE 3523