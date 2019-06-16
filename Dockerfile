FROM balenalib/raspberrypi3-debian-python:3.6-stretch

RUN apt-get update && apt-get install -y git python-pip
RUN pip install pipenv

WORKDIR /usr/src/app
COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY . .
CMD ["pipenv", "run", "python", "main.py" ]
