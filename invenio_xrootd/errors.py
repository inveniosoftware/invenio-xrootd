# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""XRootD file storage interface."""

from invenio_files_rest.errors import FilesException


class SizeRequiredError(FilesException):
    """Error thrown if no size is provided."""

    code = 400
    description = "Size of file must be provided."
