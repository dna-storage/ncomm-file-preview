# Get repo with latest python repos
FROM ubuntu:18.04

LABEL maintainer="james.m.tuck@gmail.com"

WORKDIR /preview

# Install the needed tools
RUN  apt-get update \
  && apt-get clean  \
  && apt-get install -y git python3 python3-pip zip wget \
  && apt-get clean

COPY . /preview/ncomm-file-preview    
COPY ./tools/Makefile.all /preview/Makefile
COPY ./tools/Makefile.fastq-decode-analysis /preview/fastq-decode-analysis/Makefile
COPY ./tools/Makefile.fastq-cluster-analysis /preview/fastq-cluster-analysis/Makefile

RUN python3 -m pip --no-cache-dir install -r /preview/ncomm-file-preview/requirements.txt

# Install preview cluster
RUN cd /preview \
    && git clone https://github.com/dna-storage/preview-cluster --branch v0.1.0 \
    && cd /preview/preview-cluster \
    && make -C file-sequencer-analysis init \
    && python3 -m pip --no-cache-dir install -r /preview/preview-cluster/file-sequencer-analysis/requirements.txt

# Set up data directory 
RUN cd /preview \
    && mkdir -p data \
    && cd data \
    && wget https://github.com/dna-storage/ncomm-file-preview/releases/download/v0.1-alpha/Conditions123.zip \
    && wget https://github.com/dna-storage/ncomm-file-preview/releases/download/v0.1-alpha/AllFileConditions.zip \
    && wget https://github.com/dna-storage/ncomm-file-preview/releases/download/v0.1-alpha/File1-12-2_merged.fastq.zip \
    && unzip Conditions123.zip \
    && unzip AllFileConditions.zip \
    && unzip File1-12-2_merged.fastq.zip \
    && mv File1-12-2_merged.fastq ./AllFileConditions/ \
    && rm -Rf Conditions123.zip AllFileConditions.zip 

