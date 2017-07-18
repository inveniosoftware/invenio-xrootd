# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.
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
RUN pip install --upgrade pip setuptools twine coveralls requirements-builder
RUN pip install \
    check-manifest \
    coverage \
    ipython \
    isort \
    mock \
    pydocstyle \
    pytest \
    pytest-cache \
    pytest-cov \
    pytest-pep8 \
    pytest-runner \
    Sphinx

RUN pip install XRootDPyFS "fs<2.0.0" Invenio-Files-REST[sqlite]

# Add sources to `code` and work there:
WORKDIR /code
COPY . /code

RUN requirements-builder --level=min setup.py > .travis-lowest-requirements.txt \
    && requirements-builder --level=pypi setup.py > .travis-release-requirements.txt \
    && requirements-builder --level=dev --req requirements-devel.txt setup.py > .travis-devel-requirements.txt

RUN pip install -e .[all]

RUN chown -R xrootduser:xrootduser /code && chmod a+x /code/run-docker.sh && chmod a+x /code/run-tests.sh

USER xrootduser

# Print xrootd version
RUN xrootd -v

CMD ["bash", "/code/run-docker.sh"]
