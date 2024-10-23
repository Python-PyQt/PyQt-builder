# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtGraphs':
        VersionedMetadata(version=(6, 8, 0), lgpl=False),

    'QtGraphsWidgets':
        VersionedMetadata(version=(6, 8, 0), lgpl=False),
}


class PyQt6_Graphs(AbstractPackage):
    """ The PyQt6-Graphs package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
