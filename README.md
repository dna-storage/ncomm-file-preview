# File Preview Data and Analysis


- [Overview](#overview)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [License](#license)
- [Issues](https://github.com/dna-storage/ncomm-file-preview/issues)

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
This package is supported for macOS and Linux. The package has been tested on the following systems:

+ macOS: Catalina 10.15.3
+ Linux: Ubuntu 18.04.3

Note that most OSes will support our software by using Docker.

### Software Dependences

The easiest way to satisfy all software dependences is by using Docker. If you do wish to install it in a local environment, you will need:

```
gcc 
python3
pip3
make
```

### Python Dependences

Our code has been written and tested on python versions 3.6 to 3.9. It has the following dependences:

```
nose
sphinx
biopython
editdistance
statistics
matplotlib
scipy
Pillow
bitarray
-e git+http://github.com/dna-storage/dnastorage.git@v0.9.2-alpha#egg=dnastorage
-e git+http://github.com/dna-storage/dnapreview.git#egg=dnapreview
```

# Installation Guide

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
    git clone https://github.com/dna-storage/ncomm-file-preview
    git clone https://github.com/dna-storage/preview-cluster.git
    ```

3. Install dependencies:

    ```
    cd ncomm-file-preview
    pip3 install -r requirements.txt
    ```

However, this only installs some of the software. The Docker image supports the full set of experiments.

## Use Docker

If you do not already have Docker, you will need to install Docker on your system. It is available for free for most versions of Windows, Linux, and MacOS. You may need to be the owner or administrator of the system to install Docker.

Instructions for setting up Docker.  From a command prompt, run these commands:

    git clone https://github.com/dna-storage/ncomm-file-preview
    cd ncomm-file-preview
    docker build -t preview .
    docker run -it -v `pwd`:/preview preview /bin/bash

This will bring up a command prompt in a Linux container where commands can be executed. 

## Run Our Analyses

From inside the Docker container, run the following command to perform analyses and generate the raw data:

```
make all
```

# License

This software is released under the MIT License.

