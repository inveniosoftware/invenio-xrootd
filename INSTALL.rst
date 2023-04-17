..
    This file is part of Invenio.
    Copyright (C) 2016-2023 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============

Install from PyPI::

    pip install invenio-xrootd

.. note::

   Invenio-XRootD is dependent on
   `XRootDPyFS <http://xrootdpyfs.readthedocs.io/>`_ and the XRootD Python
   bindings which can be somewhat difficult to install.
   Please consult the XRootDPyFS installation guide for further details.


Running tests
-------------
The easiest way of running the tests is via Docker due to the difficulties in
installing the Python XRootD bindings locally.

Build the image:

.. code-block:: console

   $ docker build --platform linux/amd64 --build-arg xrootd_version=4.12.7  -t invxrootd --progress=plain .

Run the container:

.. code-block:: console

   $ docker run --platform linux/amd64 -h invxrootd -it -v <absolute path to this project>:/code invxrootd bash

You will the logs in the stdout. Next, in another shell, connect the container
and fire up an ipython shell:

.. code-block:: console

   $ docker ps  # find the container id
   $ docker exec -it <container-id> bash
   [invxrootd@invxrootd code]$ ipython

