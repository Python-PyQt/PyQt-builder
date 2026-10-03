# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2026 Phil Thompson <phil@riverbankcomputing.com>


from ..abstract_package import AbstractPackage
from ..qt_metadata import VersionedMetadata


# The Qt meta-data for this package.
_QT_METADATA = {
    'QtCanvasPainter':
        VersionedMetadata(version=(6, 12, 0), lgpl=False),
}


class PyQt6_CanvasPainter(AbstractPackage):
    """ The PyQt6-CanvasPainter package. """

    def get_qt_metadata(self):
        """ Return the package-specific meta-data describing the parts of Qt to
        install.
        """

        return _QT_METADATA
