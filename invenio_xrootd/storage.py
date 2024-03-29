# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""XRootD file storage interface."""

from functools import wraps

from flask import current_app
from fs.errors import Unsupported
from fs.path import basename, dirname
from invenio_files_rest.storage.pyfs import PyFSFileStorage, pyfs_storage_factory
from xrootdpyfs import XRootDPyFS

from .errors import SizeRequiredError


class XRootDFileStorage(PyFSFileStorage):
    """File system storage using XRootD for accessing files.

    XRootD v3.x are only capable of reporting adler32 checksums, even though
    that the storage system will report e.g. a MD5 checksums. If this is the
    case, set the configuration variable ``XROOTD_CHECKSUM_ALOG`` to overwrite
    the algorithm name reported by the XRootD server.
    """

    def __init__(self, fileurl, **kwargs):
        """Initialize file storage object."""
        # Overwrite reported checksum algorithm.
        self.checksum_algo = (
            current_app.config.get("XROOTD_CHECKSUM_ALGO") if current_app else None
        )
        super().__init__(fileurl, **kwargs)

    def _get_fs(self, create_dir=True, query=None):
        """Get PyFilesystem instance and path."""
        # Fall-back to PyFS in case of non-xrootd URL
        if not self.fileurl.startswith(("root://", "roots://")):
            return super()._get_fs(create_dir=create_dir)
        filedir = dirname(self.fileurl)
        filename = basename(self.fileurl)

        if query is None:
            fs = XRootDPyFS(filedir)
        else:
            fs = XRootDPyFS(filedir, query)

        if create_dir:
            fs.makedir("", recursive=True, allow_recreate=True)

        return (fs, filename)

    def checksum(self, chunk_size=None, progress_callback=None, use_default_impl=False):
        """Compute checksum of file.

        Queries the XRootD server to get checksum if possible, otherwise falls
        back to default Python implementation. The checksum algorithm used
        will be the one configured on the XRootD server.
        """
        if use_default_impl:
            return super().checksum(
                chunk_size=chunk_size,
                progress_callback=progress_callback,
            )
        try:
            fs, path = self._get_fs()
            if not hasattr(fs, "xrd_checksum"):
                raise Unsupported()
            algo, val = fs.xrd_checksum(path)
            return "{0}:{1}".format(self.checksum_algo or algo, val)
        except Unsupported:
            return super().checksum(
                chunk_size=chunk_size,
                progress_callback=progress_callback,
            )


def ensure_bookingsize(with_arg=False):
    """Decorator to set ``eos.bookingsize``."""

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            self.set_bookingsize(
                kwargs.get("size", args[0] if args and with_arg else None)
            )
            res = f(self, *args, **kwargs)
            self.bookingsize = None
            return res

        return inner

    return decorator


class EOSFileStorage(XRootDFileStorage):
    """File storage for CERN EOS via XRootD.

    EOS needs to know the file size upfront in order to allocate your
    file to disk servers with enough available space. This is done by providing
    ``eos.bookingsize=xyz`` in the root URL.

    This file storage module takes care of setting the booking size for
    initialize and save operations.

    If you use this file storage class, it also means that your REST API
    clients **must** provide the file size upfront.
    """

    def __init__(self, fileurl, default_booking_size=None, **kwargs):
        """Initialize storage."""
        self.bookingsize = None
        self.default_booking_size = default_booking_size or (
            current_app.config.get("MAX_CONTENT_LENGTH") if current_app else None
        )
        super().__init__(fileurl, **kwargs)

    def set_bookingsize(self, size):
        """Set EOS booking size.

        Ensures that EOS will allocate the file to disk server with enough
        available space.
        """
        if size is None and self.default_booking_size is None:
            raise SizeRequiredError()
        self.bookingsize = size or self.default_booking_size

    def _get_fs(self, create_dir=True):
        """Get PyFilesystem instance and path."""
        query = {}
        if self.bookingsize:
            query["eos.bookingsize"] = self.bookingsize

        return super()._get_fs(create_dir=create_dir, query=query)

    @ensure_bookingsize(with_arg=True)
    def initialize(self, *args, **kwargs):
        """Initialize file of given size.

        Set the ``eos.bookingsize`` variable in the root URL, to ensure EOS
        allocates the file to a disk server with enough space.
        """
        return super().initialize(*args, **kwargs)

    @ensure_bookingsize()
    def save(self, *args, **kwargs):
        """Initialize file of given size.

        Set the ``eos.bookingsize`` variable in the root URL, to ensure EOS
        allocates the file to a disk server with enough space.
        """
        return super().save(*args, **kwargs)


def xrootd_storage_factory(**kwargs):
    """File storage factory for XRootD."""
    return pyfs_storage_factory(filestorage_class=XRootDFileStorage, **kwargs)


def eos_storage_factory(**kwargs):
    """File storage factory for EOS."""
    return pyfs_storage_factory(filestorage_class=EOSFileStorage, **kwargs)
