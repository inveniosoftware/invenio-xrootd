# SPDX-FileCopyrightText: 2017-2019 CERN.
# SPDX-License-Identifier: MIT

"""Flask extension for Invenio-XRootD."""

from pkg_resources import DistributionNotFound, get_distribution

try:
    # Import XRootDPyFS if available so that its
    # opener gets registered on PyFilesystem.
    get_distribution("xrootdpyfs")
    import xrootdpyfs

    XROOTD_ENABLED = True
except DistributionNotFound:
    XROOTD_ENABLED = False
    xrootdpyfs = None


class InvenioXRootD(object):
    """Invenio-XRootD extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Extension registration and configuration."""
        app.config.setdefault("XROOTD_ENABLED", XROOTD_ENABLED)
        if XROOTD_ENABLED:
            app.config.setdefault(
                "FILES_REST_STORAGE_FACTORY", "invenio_xrootd:eos_storage_factory"
            )
        app.extensions["invenio-xrootd"] = self
