# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtDataVisualization':
        VersionedMetadata(lgpl=False),
}


class PyQtDataVisualization(AbstractPackage):
    """ The PyQtDataVisualization package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
