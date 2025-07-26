FROM python:3.14.0rc1-alpine3.22

ADD . /src

WORKDIR /src

RUN pip install --upgrade pip setuptools wheel
RUN python3 setup.py install

ENTRYPOINT ["gixy"]
