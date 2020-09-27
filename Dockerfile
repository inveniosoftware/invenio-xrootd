# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# Dockerfile for running Invenio-XRootD tests.
#
# Usage:
#   docker build -t xrootd . && docker run -h xrootdhost -it xrootd

FROM centos:7

# Install xrootd
RUN rpm -Uvh http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

RUN yum install -y \
    gcc \
    python-devel \
    xrootd \
    xrootd-client \
    xrootd-client-devel \
    xrootd-python git \
    xrootd-server \

RUN yum install -y python-pip

RUN adduser --uid 1001 xrootduser

# Install some prerequisites ahead of `setup.py` in order to profit
# from the docker build cache:
RUN pip install --upgrade pip
RUN pip install setuptools py twine wheel coveralls requirements-builder
RUN pip install XRootDPyFS "fs<2.0.0" Invenio-Files-REST[sqlite]

# Add sources to `code` and work there:
WORKDIR /code
COPY . /code

RUN pip install -e .[all]

RUN chown -R xrootduser:xrootduser /code && chmod a+x /code/run-docker.sh && chmod a+x /code/run-tests.sh

USER xrootduser

# Print xrootd version
RUN xrootd -v

CMD ["bash", "/code/run-docker.sh"]
