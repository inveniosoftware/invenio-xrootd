# SPDX-FileCopyrightText: 2016-2019 CERN.
# SPDX-License-Identifier: MIT

"""XRootD file storage interface."""

from invenio_files_rest.errors import FilesException


class SizeRequiredError(FilesException):
    """Error thrown if no size is provided."""

    code = 400
    description = "Size of file must be provided."
