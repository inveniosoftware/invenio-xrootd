# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Pytest configuration."""

import hashlib
import shutil
import tempfile
from functools import wraps
from os import makedirs
from os.path import dirname, join

import pytest
from flask import Flask

from invenio_xrootd import EOSFileStorage, XRootDFileStorage


@pytest.fixture
def BytesIO():
    """IO instance."""
    try:
        from io import BytesIO

        return BytesIO
    except ImportError:
        from StringIO import StringIO

        return StringIO


@pytest.yield_fixture()
def app():
    """Flask application fixture."""
    app = Flask("testapp")
    app.config.update(TESTING=True, MAX_CONTENT_LENGTH=10, XROOTD_CHECKSUM_ALGO="md5")
    with app.app_context():
        yield app


@pytest.fixture
def mkurl():
    """Generate test root URL."""
    return lambda p: "root://localhost/{0}".format(p)


@pytest.yield_fixture
def tmppath():
    """Temporary path."""
    path = tempfile.mkdtemp()
    # shutil.copytree(join(dirname(__file__), "data"), join(path, "data"))
    yield path
    shutil.rmtree(path)


@pytest.fixture
def file_path(tmppath):
    """File path."""
    return join(tmppath, "a/b/testfile")


@pytest.fixture
def file_url(file_path, mkurl):
    """File URL."""
    return mkurl(file_path)


@pytest.fixture
def file_content(file_path):
    """File content."""
    makedirs(dirname(file_path))
    data = b"test"
    with open(file_path, "wb") as fp:
        fp.write(data)
    return data


@pytest.fixture
def file_md5(file_content):
    """Checksum of content."""
    m = hashlib.md5()
    m.update(file_content)
    return str(m.hexdigest())


@pytest.fixture
def xrd_storage(file_url):
    """Storage instance for XRootDFileStorage."""
    return XRootDFileStorage(file_url)


@pytest.fixture
def xrd_storage_ospath(file_path):
    """Storage instance for XRootDFileStorage with OS path."""
    return XRootDFileStorage(file_path)


@pytest.fixture
def xrd_storage_mocked(file_url, file_md5):
    """Patch xrd_checksum."""
    # Since local xrootd server can't compute checksums.
    xrd_storage = XRootDFileStorage(file_url)
    f = xrd_storage._get_fs

    @wraps(f)
    def mock(*args, **kwargs):
        fs, filename = f(*args, **kwargs)

        def xrd_checksum(*args, **kwargs):
            return "adler32", file_md5

        fs.xrd_checksum = xrd_checksum
        return fs, filename

    xrd_storage._get_fs = mock

    return xrd_storage


@pytest.fixture
def eos_storage(file_url):
    """EOS storage instance."""
    return EOSFileStorage(file_url)


@pytest.fixture
def file_instance_mock(file_url):
    """Mock of a file instance."""

    class FileInstance(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    return FileInstance(uri=file_url, size=4, updated=None)
