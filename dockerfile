# docker pull python:3.7.3
# docker build -t midsc .
# docker run -p 3523:3523 midsc
FROM python:3.7.3
WORKDIR /
MAINTAINER lsd200
RUN mkdir -p midsc
COPY ./ /midsc/
RUN pip install --upgrade pip && pip install -r midsc/requirements.txt
WORKDIR /midsc/src/
EXPOSE 3523
CMD ["python","container.py"]