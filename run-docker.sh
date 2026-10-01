#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2015-2026 CERN.
# SPDX-License-Identifier: MIT

# xrootd only accepts config directives via -c <file>, so we write the
# single directive needed for tests (adler32 checksum support, used by
# test_checksum) to a temporary file. Process substitution (<(...)) does not
# work: xrootd re-reads the config file and, with -b, opens it after
# daemonizing, when the /dev/fd/NN pipe is no longer available.
XROOTD_CFG="$(mktemp)"
echo "xrootd.chksum md5" > "$XROOTD_CFG"
xrootd -c "$XROOTD_CFG" -b && ./run-tests.sh
