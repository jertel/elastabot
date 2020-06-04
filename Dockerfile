FROM alpine

LABEL description="SlackBot for Elastalert"
LABEL maintainer="Jason Ertel (jertel at codesim.com)"

RUN apk --update upgrade && \
    apk add ca-certificates gcc python3-dev musl-dev py3-pip openssl && \
    rm -rf /var/cache/apk/*

RUN pip install elasticsearch slackclient

COPY src/* /opt/elastabot/

WORKDIR /opt/elastabot

ENTRYPOINT ["python", "/opt/elastabot/elastabot.py"]