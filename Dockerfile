FROM ubuntu:20.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    vim && \
    apt-get clean

RUN mkdir /code
ADD requirements.txt /code
RUN /usr/bin/python3.9 -m pip install -r /code/requirements.txt
ADD . /code
WORKDIR /code
CMD ["./start.sh"]