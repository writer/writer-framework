FROM python:3-slim AS compile-image
RUN apt-get update -y && mkdir /app && python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
COPY . /app
WORKDIR /app
RUN pip3 install 'streamsync[ds]' && pip3 install -r requirements.txt

FROM python:3-slim AS run-image
RUN apt-get update -y && mkdir /app
COPY --from=compile-image /app /app
ENV PATH="/app/venv/bin:$PATH"
WORKDIR /app

ENTRYPOINT [ "streamsync", "run" ]
EXPOSE 5000
CMD [ ".",  "--port", "5000", "--host", "0.0.0.0" ]