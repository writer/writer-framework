FROM ubuntu:20.04

RUN apt-get update -y && \
    apt upgrade -y && apt-get update && \ 
    apt-get install -y python3-pip python3-dev curl sudo

RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./server /app

ENTRYPOINT [ "python3", "app.py" ]

EXPOSE 5000

CMD [ "user_script" ]