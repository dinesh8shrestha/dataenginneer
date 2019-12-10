FROM ubuntu:18.04
MAINTAINER Artem
RUN apt-get clean && apt-get update -y && apt-get install -y python-pip python-dev build-essential
COPY requirements.txt /flask-app
RUN pip install -r requirements.txt
COPY . /flask-app
WORKDIR /flask-app
ENTRYPOINT ["python"]
CMD ["lab03_service.py"]
