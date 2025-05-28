FROM python:3.10

WORKDIR /nebula
COPY . .

#ENV SOCKS4_PROXY="127.0.0.1:1080"

#ADD /etc/proxychains.conf /etc/proxychains.conf



RUN apt-get update && apt-get upgrade -y
RUN apt install python3-dev -y
RUN apt install docker.io -y
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN apt update && apt install awscli -y
RUN apt update && apt install proxychains4 -y
RUN apt-get update; apt-get install curl -y
RUN curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
RUN dpkg -i session-manager-plugin.deb
RUN service docker start

RUN apt-get update && apt-get install -y \
    wget \
    git \
    gcc \
    make \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

ENV GO_VERSION=1.22.3
RUN curl -OL https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH=/go
RUN mkdir -p /go/bin

EXPOSE 5000

#ENTRYPOINT ["proxychains4", "python3", "teamserver.py"]
ENTRYPOINT ["python3", "teamserver.py"]
