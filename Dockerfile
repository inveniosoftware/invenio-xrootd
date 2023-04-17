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

RUN yum install -y git wget epel-release
RUN yum group install -y "Development Tools"

# Install and set python3.6 as default
RUN yum install -y centos-release-scl && \
    yum install -y rh-python36
RUN echo '#!/bin/bash' >> /etc/profile.d/enablepython36.sh && \
    echo '. scl_source enable rh-python36' >> /etc/profile.d/enablepython36.sh
ENV BASH_ENV=/etc/profile.d/enablepython36.sh

RUN chmod -R g=u /etc/profile.d/enablepython36.sh /opt/rh/rh-python36 && \
    chgrp -R 0 /etc/profile.d/enablepython36.sh /opt/rh/rh-python36
SHELL ["/bin/bash", "-c"]

RUN yum-config-manager --enable rhel-server-rhscl-7-rpms
RUN yum install -y devtoolset-7
RUN scl enable devtoolset-7 bash

# Install xrootd
ARG xrootd_version=""
ARG cmake="cmake3"
RUN yum-config-manager --add-repo https://xrootd.slac.stanford.edu/binaries/xrootd-stable-slc7.repo
RUN if [ ! -z "$xrootd_version" ] ; then XROOTD_V="-$xrootd_version" ; else XROOTD_V="" ; fi && \
    echo "Will install xrootd version: $XROOTD_V (latest if empty)" && \
    yum --setopt=obsoletes=0 install -y "$cmake" \
                                        gcc-c++ \
                                        zlib-devel \
                                        openssl-devel \
                                        libuuid-devel \
                                        python3-devel \
                                        xrootd"$XROOTD_V"

RUN pip install --upgrade "pip<20" "setuptools<58" wheel

# Install Python xrootd and fs
# Ensure that installed version of xrootd Python client is the same as the RPM package
RUN rpm --queryformat "%{VERSION}" -q xrootd
RUN XROOTD_V=`rpm --queryformat "%{VERSION}" -q xrootd` && \
    echo "RPM xrootd version installed: $XROOTD_V" && \
    pip install xrootd=="$XROOTD_V"

WORKDIR /code
COPY . /code

RUN pip install -e '.[tests]'
RUN pip freeze

RUN adduser --uid 1001 xrootduser
RUN chown -R xrootduser:xrootduser /code
RUN chmod a+x /code/run-docker.sh
RUN chmod a+x /code/run-tests.sh

USER xrootduser

# Print xrootd version
RUN XROOTD_V=`xrootd -v` && echo "xrootd version when running it: $XROOTD_V"

CMD ["bash", "/code/run-docker.sh"]
