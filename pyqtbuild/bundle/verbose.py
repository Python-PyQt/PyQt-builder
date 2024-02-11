# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


# Set if verbose error messages are enabled.
_verbose = False


def is_verbose():
    """ Return True if verbose progress messages are enabled. """

    return _verbose


def set_verbose(verbose):
    """ Enable or disable verbose progress messages. """

    global _verbose
    _verbose = verbose


def verbose(message):
    """ Display a verbose progress message. """

    if _verbose:
        if message[-1] != '.':
            message += '...'

        print(message, flush=True)
