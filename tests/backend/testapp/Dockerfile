FROM ubuntu:22.04

RUN apt-get update -y && \
    apt upgrade -y && apt-get update && \ 
    apt-get install -y python3-pip python3-dev curl sudo

RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install writer==0.1.2
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "writer", "run" ]

EXPOSE 5000

CMD [ ".",  "--port", "5000", "--host", "0.0.0.0" ]