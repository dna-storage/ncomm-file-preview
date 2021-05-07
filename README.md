# File Preview Data and Analysis

[![Build Status](https://travis-ci.com/dna-storage/ncomm-file-preview.svg?branch=main)](https://travis-ci.com/dna-storage/ncomm-file-preview)

- [Overview](#overview)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [License](#license)
- [Issues](https://github.com/dna-storage/ncomm-file-preview/issues)
- [Data Download](#data-downloads)

# Overview

Scripts and data in support of "preview" operations in a pending manuscript. This is the main repository and relies on two others:
   ```
   github.com/dna-storage/dnapreview.git
   github.com/dna-storage/preview-cluster.git
   ```

# Documentation

As documentation for the software becomes available, it will be placed under the docs folder.

# System Requirements

## Hardware Requirements
This code will run on a standard computer with modest RAM and compute speed. However, some aspects of the analysis, such as the clustering analysis we perform, are greatly sped-up by access to a high performance computing system. Details can be found in the associated repositories, namely github.com/dna-storage/preview-cluster.git.

## Software Requirements
### OS Requirements
This package is supported on Linux. The package has been tested on the following systems:

+ Linux: Ubuntu 18.04.3

Note that other OSes or versions will support our software by using Docker with our provided Dockerfiles.

### Software Dependences

The easiest way to satisfy all software dependences is by using Docker. If you do wish to install it in a local environment, you will need:

```
gcc 
python3
pip3
make
```

### Python Dependences

Our python code has been written and tested on multiple python versions from 3.6 to 3.9. But, these requirements are specified to match our Dockerfile which uses python 3.6.9. It has the following dependences:

```
nose
sphinx
editdistance
statistics
numpy==1.19.5
matplotlib==3.3.0
scipy==1.5.4
biopython
Pillow
bitarray==1.9.2
dnastorage==0.9.4
-e git+http://github.com/dna-storage/dnapreview.git#egg=dnapreview
```

# Installation Guide

For a quick start, the recommended approach is to use Docker.  But, it should be possible to compile and run the software on most systems.

## Use your local environment 

For a partial install of this repo, you simply use python 3 already installed on your system.

1. First, create a suitable virtual environment. Make directory and create a virtual environment for python:

    ```
    mkdir -p preview
    cd preview
    python3 -m venv env
    source env/bin/activate
    ```

2. Next, download or clone the repos:

    ```    
    git clone https://github.com/dna-storage/ncomm-file-preview.git
    git clone https://github.com/dna-storage/preview-cluster.git
    ```

3. Install software and dependencies:

    ```
    cd ncomm-file-preview
    pip3 install -r requirements.txt
    cd ../preview-cluster
    make -C file-sequencer-analysis init
    pip3 install -r file-sequencer-analysis/requirements.txt	

    ```

## Use Docker

If you do not already have Docker, you will need to install Docker on your system. It is available for free for most versions of Windows, Linux, and MacOS. You may need to be the owner or administrator of the system to install Docker.

Instructions for setting up Docker. Note, this process may take upwards of 10 minutes, depending on the speed of your system and network. The last docker build command takes the longest time. From a command prompt, run these commands:

    git clone https://github.com/dna-storage/ncomm-file-preview
    cd ncomm-file-preview
    docker build -t preview .
    docker run -it -v `pwd`:/preview preview /bin/bash

This will bring up a command prompt in a Linux container where commands can be executed. 

## Reproduce Our Analyses

From inside the Docker container, run the following command to perform analyses and generate the raw data. This command may take several hours to complete.

```
make all
```

The preview encoded library can be found within the container after running make. Note, this library is regenerated from scratch and may slightly differ from the one used in the paper due to differences in dependent software libraries:
```
/preview/ncomm-file-preview/library
```

The data produced by analyzing fastq files can be found in these two directories within the container:
```
/preview/fastq-decode-analysis
/preview/fastq-cluster-analysis

```

# Data Downloads

Download the raw experimental data from release [v0.1-alpha](https://github.com/dna-storage/ncomm-file-preview/releases/tag/v0.1-alpha).

# License

This software is released under the MIT License.

