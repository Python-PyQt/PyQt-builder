# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from sipbuild import Installable


class QmakeTargetInstallable(Installable):
    """ An installable for the TARGET of a .pro file.  A TARGET is installed
    automatically but this captures the information needed for the .dist-info
    directory.
    """

    def __init__(self, target, target_subdir):
        """ Initialise the installable. """

        super().__init__('target', target_subdir=target_subdir)

        self.files.append(target)
