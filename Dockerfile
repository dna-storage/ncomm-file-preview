# Get repo with latest python repos
FROM ubuntu:18.04

LABEL maintainer="james.m.tuck@gmail.com"

WORKDIR /preview

# Install the needed tools
RUN  apt-get update \
  && apt-get clean  \
  && apt-get install -y git python3 python3-pip \
  && apt-get clean

COPY . /preview/ncomm-file-preview    
COPY ./tools/Makefile.all /preview/Makefile

RUN pip3 --no-cache-dir install -r /preview/ncomm-file-preview/requirements.txt

RUN cd /preview \
    && git clone https://github.com/dna-storage/preview-cluster \
    && cd /preview/preview-cluster \
    && make -C file-sequencer-analysis init


# Set python path to include the code in the preview folder
ENV "PYTHONPATH" "/preview/"
