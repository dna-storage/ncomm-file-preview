# Get repo with latest python repos
FROM python:latest

LABEL maintainer="james.m.tuck@gmail.com"

WORKDIR /preview

COPY . .

# Install the needed tools
RUN pip3 --no-cache-dir install -r requirements.txt

# Set python path to include the code in the preview folder
ENV "PYTHONPATH" "/preview/"
