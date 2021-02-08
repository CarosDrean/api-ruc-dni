FROM ubuntu:20.04

WORKDIR /code

ENV APP app.py
ENV APP_RUN_HOST 0.0.0.0

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get install -y libgl1-mesa-glx
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install libgtk2.0-dev
RUN apt-get install -y libleptonica-dev
RUN apt-get install -y tesseract-ocr
RUN apt-get install -y libtesseract-dev


COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]
