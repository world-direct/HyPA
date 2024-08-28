ARG SIPP_VERSION="3.7.2"

FROM r.world-direct.at/dockerhub/library/ubuntu:20.04 as builder

ARG SIPP_VERSION

RUN apt-get -y update && \
    apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    net-tools \
    libssl-dev \
    libpcap-dev \
    libsctp-dev \
    libncurses5-dev \
    vim \
    wget
RUN wget https://github.com/SIPp/sipp/releases/download/v${SIPP_VERSION}/sipp-$SIPP_VERSION.tar.gz
RUN  tar -xzf /sipp-$SIPP_VERSION.tar.gz
WORKDIR /sipp-$SIPP_VERSION
RUN cmake . -DUSE_SSL=1 -DUSE_SCTP=1 -DUSE_PCAP=1 -DUSE_GSL=1 && make

FROM r.world-direct.at/dockerhub/library/ubuntu:20.04

ARG SIPP_VERSION

RUN apt-get update -y && \
    apt-get install -y \
    libssl1.1 \
    libpcap0.8 \
    libsctp1 \
    vim

COPY --from=builder /sipp-$SIPP_VERSION/sipp /usr/bin/sipp

VOLUME /scenarios/test/

WORKDIR /scenarios

ADD scenarios/ /scenarios/

RUN mkdir /scenarios/test/
RUN chmod -R 777 /scenarios/

ENTRYPOINT ["sipp"]
