# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtDataVisualization': (
        # It's likely that the QML library was required from the start.
        VersionedMetadata(version=(6, 5, 0),
                lib_deps={'': ('QtDataVisualizationQml', )},
                qml=True, lgpl=False),
        VersionedMetadata(version=(6, 1, 0), qml=True, lgpl=False))
}


class PyQt6_DataVisualization(AbstractPackage):
    """ The PyQt6-DataVisualization package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
