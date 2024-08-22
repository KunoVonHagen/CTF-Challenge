FROM docker:18.09.1-dind

ARG MONITORING_HOST_FLAG_SECRET

RUN apk update
RUN apk add gcc
RUN apk add wget
RUN apk add curl
RUN apk add build-base
RUN apk add openssl
RUN apk add openssl-dev

RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-2.30-r0.apk
RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-bin-2.30-r0.apk
RUN wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.30-r0/glibc-i18n-2.30-r0.apk

RUN apk add --no-cache --allow-untrusted glibc-2.30-r0.apk glibc-bin-2.30-r0.apk glibc-i18n-2.30-r0.apk

WORKDIR /root

COPY . /root/

RUN chmod +x /root/setup_monitoring.sh

RUN echo $MONITORING_HOST_FLAG_SECRET > /root/secret.txt

RUN gcc -o /root/get_flag /root/get_flag.c -lssl -lcrypto
RUN chmod 550 /root/get_flag
RUN rm /root/get_flag.c

CMD /root/setup_monitoring.sh & dockerd
