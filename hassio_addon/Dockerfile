ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache make gcc musl-dev tshark libusb-dev libxslt python3 py3-pip && pip3 install paho-mqtt
RUN curl -L https://github.com/homewsn/whsniff/archive/v1.3.tar.gz -o /tmp/whsniff-1.3.tar.gz && \
    echo "e1de4c74ddb68e2744af207a6df395a2ab2f51bd203ba348a935fa39895f2309  /tmp/whsniff-1.3.tar.gz" | sha256sum -cw && \
    tar -C / -xzf /tmp/whsniff-1.3.tar.gz && \
    cd /whsniff-1.3 && make

COPY rootfs /
